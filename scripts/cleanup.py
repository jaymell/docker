#!/usr/bin/python

"""
run-time parameters
    -- list of image IDs to exclude
    -- list of image TAGs to exclude

#algorithm:
. get _all_ containers by ID
	if preserve_running:
	. get image TAGS _AND_ IDs used by running containers
		-- making sure we exclude both from image deletion will prevent running containers
			from having the tag they're using removed -- the container continues running,
			but it will lose the reference to the image tag it's using, which sucks 
	. remove running container IDs from list
	. remove any container excludes passed at runtime
	. "docker rm" all containers left in list

. get images (not intermediate) -- both TAGS and IDs, probably
	if preserve_running:
		remove TAGs associated with running containers from list 
		remove IDs associated with running containers from list 
	. remove any image excludes passed at runtime
	. since runtime excludes may be either tags or (short or long) IDs,
		need a way to find associated tags (IDs) based on the ID (tag)
		that was passed and remove those from deletion lists as well
	. remove all image TAGs left in list
	. remove all image IDs left in list
		. repeat -- looping back through and deleting any
			which previously failed because of child images
		. repeat until you hit MAX_ATTEMPTS or because all have been deleted

. Limitations and Weirdnesses
    since tags deleted before IDs, and IDs list gets created before Tags list is 
        deleted, there will likely be lots of errors once it starts deleting IDs,
        since many will have already been deleted by iterating through tags
    also, associated IDs are not removed when tags are specified, so it will
        try and fail to delete those IDs ... probably should be cleaned up
"""

import sys
import docker
import time
import argparse
import re

"""
# install deps on amazon-linux:
sudo yum install -y python27-pip.noarch
sudo pip-2.7 install docker-py
"""

def remove_the_nones(image_tag_list):
	""" remove the nones"""

	images = [ i for i in image_tag_list if '<none>:<none>' not in i ]
	return images

def exclude_image_tags(image_list, images_to_exclude, all_images):
    """ because tags and repos are ambiguous, don't assume to know
        which one was intended... regex either """
        
    deletions = []
    ids_to_exclude = []
    for exclude in images_to_exclude:
            for img in image_list:
                match = re.search('.*%s.*' % exclude, img)
                # if the exclude matches an entry in the deletion list:
                if match: 
                    print("Skipping tag %s" % img)
                    deletions.append(img)

    images = [ i for i in image_list if i not in deletions ]

    for deletion in deletions:
        for img in all_images:
            if type(img['RepoTags']) == list and deletion in img['RepoTags']:
               ids_to_exclude.append(img['Id'])
 
    return (images, ids_to_exclude)

def exclude_image_ids(image_list, images_to_exclude, all_images):
    """ a little more involved; 1) since short image names may be
        passed, use regex to match against full image name; 2) I'm 
        assuming we want to preserve tags associated with image IDs
        to preserve, so find associated image tags and return those
        as well so they can be removed from del_image_tags, which
        is why all_images must be passed """

    deletions = []
    tags_to_exclude = []
    for exclude in images_to_exclude:
    	for img in image_list:
    		match = re.search('.*%s.*' % exclude, img)
    		# if the exclude matches an entry in the deletion list:
    		if match: 
                        print("Skipping ID %s" % img)
                        deletions.append(img)

    images = [ i for i in image_list if i not in deletions ]	
    
    for deletion in deletions:
            for img in all_images:
                    if img['Id'] == deletion:
                            tags_to_exclude.extend([i for i in img['RepoTags'] if type(img['RepoTags']) == list])
    
    return (images, tags_to_exclude)


def remove_containers(client, container_list, Force=False, execute=False):
    """ remove containers -- nothing fancy, since this generally
        works -- Force=True if you want to remove moving containers
        as well """

    if not container_list:
        print("Container list is empty!")
        return
    for ct in del_container_ids:
    # set force=False just in case to prevent accidental container deletion, 
    # even though above logic should already have removed them from deletion list:
        try:
            print("Deleting container %s" % ct)
            if execute: client.remove_container(container=ct, force=Force)
        except Exception as e:
            print('Failed to remove container %s: %s' % (ct,e))

def remove_images(client, image_list, num_attempts, execute=False):
	""" take a list of either images or tags and, assuming the list
		isn't empty, attempt to delete them one by one -- remove successful
		ones from list """
	
	if not image_list: 
		print("Image list is empty!")
		return 

	attempt_count = 1
	while attempt_count <= num_attempts and len(image_list) > 0:
		successes = []
		for img in image_list:
			try:
				print("Deleting img tag %s" % img)
				if execute: client.remove_image(image=img)
			except Exception as e:
				print('Failed to remove image tag %s: %s' % (img,e))
			else:
				successes.append(img)
		[ image_list.remove(i) for i in successes ]
		attempt_count += 1


if __name__ == '__main__':

	MAX_ATTEMPTS = 10

	cli = docker.Client(version='auto')

	parser = argparse.ArgumentParser(description='Delete old images and containers on Docker hosts')
	parser.add_argument('--preserve-running', "-p", default = False, action = 'store_true',	
						help="If true, preserve running containers and the images associated with them. Default is False")
	parser.add_argument('--num-days', '-n', default = 0, 
						help= """ Specify minimum number of days old  an image
						or container must be before deleting it. Default is 0 """
					   )
	parser.add_argument("--exclude-image-tag", "-t", nargs="+", help="Exclude specified Image __Tags__")
	parser.add_argument("--exclude-image-id", "-i", nargs="+", help="Exclude specified Image __IDs__")
	parser.add_argument("--execute", "-x", action = "store_true", default=False, help="This is how you actually run it, heh")
	args = parser.parse_args()

        #### if execute False, don't actually delete stuff -- False by default
        execute = args.execute
        if not execute:
            print("\n****************DRY RUN ONLY****************\n")
        else:
            print("\n****************ACTUALLY DELETING STUFF!****\n")
        

	# in case we just want to delete images older than certain threshold, ie 10 days:
	one_day = 86400
	num_days = args.num_days
	time_threshold = num_days * one_day
	unix_time = time.time() 

	running_containers = cli.containers(all=False)
	running_container_ids = [ i['Id'] for i in running_containers ]
	all_containers = cli.containers(all=True)
	all_container_ids = [ i['Id'] for i in all_containers ]

	# technically not ALL images, but hopfully we won't
	# have to worry with intermediate images .... we shall see:
	all_images = cli.images()
	all_image_ids = { i['Id'] for i in all_images }
	all_image_tags = { j for i in all_images for j in i['RepoTags'] if type(i['RepoTags']) == list }
	used_image_ids = { i['ImageID'] for i in running_containers }
	used_image_tags = { i['Image'] for i in running_containers }

	del_container_ids = [ i for i in all_container_ids if (unix_time - i['Created']) > time_threshold ]
	del_image_tags = { j for i in all_images for j in i['RepoTags'] if type(i['RepoTags']) == list and (unix_time - i['Created']) > time_threshold }
	del_image_ids = [ i['Id'] for i in all_images if (unix_time - i['Created']) > time_threshold ]

	# only exclude running containers on ecs host:	
	if args.preserve_running:
		print("Preserving running containers and associated images... ")
		del_container_ids = [ i for i in del_container_ids if i not in running_container_ids ]
		del_image_tags, unused = exclude_image_tags(del_image_tags, used_image_tags, all_images)
		del_image_ids, unused = exclude_image_ids(del_image_ids, used_image_ids, all_images)
	else:
		print("Attempting to delete ALL containers and images, minus CLI exclusions... ")

	additional_tag_excludes = None
	additional_id_excludes = None
	if args.exclude_image_tag:
		del_image_tags, additional_id_excludes = exclude_image_tags(del_image_tags, args.exclude_image_tag, all_images)
	if args.exclude_image_id:
		del_image_ids, additional_tag_excludes = exclude_image_ids(del_image_ids, args.exclude_image_id, all_images)	
	# this is sloppy -- take the TAGs returned by exclude_image_ids
        # and make sure they're taken out of the to-be-deleted list:
	if additional_tag_excludes:
		del_image_tags, unused = exclude_image_tags(del_image_tags, additional_tag_excludes, all_images)
	if additional_id_excludes:
		del_image_ids, unused = exclude_image_ids(del_image_ids, additional_id_excludes, all_images)

        # remove containers:
        Force = False if args.preserve_running else True
        if del_container_ids:
            remove_containers(cli, del_container_ids, Force=Force, execute=execute)
        
	# remove the <None:None> from tag list:
	del_image_tags = remove_the_nones(del_image_tags)

	# remove images by tag first:
        if del_image_tags:
            
            remove_images(cli, del_image_tags, MAX_ATTEMPTS, execute=execute)

	# then by ID:
        if del_image_ids:
            remove_images(cli, del_image_ids, MAX_ATTEMPTS, execute=execute)


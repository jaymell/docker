#!/usr/bin/python

"""
run-time parameters
	-- list of container IDs to exclude
	-- list of image IDs to exclude

. get _all_ containers by ID
	if ecs host:
	. get image TAGS _AND_ IDs used by running containers
		-- making sure we exclude both from image deletion will prevent running containers
			from having the tag they're using removed -- the container continues running,
			but it will lose the reference to the image tag it's using, which sucks 
	. remove running container IDs from list
	. remove any container excludes passed at runtime
	. "docker rm" all containers left in list

. get images (not intermediate) -- both TAGS and IDs, probably
	if build host:
		remove ones with certain tags from list  -- get via jenkins request?
	if ecs host:
		remove TAGs associated with running containers from list 
		remove IDs associated with running containers from list 
	. remove any image excludes passed at runtime
	. remove all image TAGS left in list
	. remove all image IDs left in list
		. repeat -- _hopfully_ doing so will allow to loop back through and delete any
			which previously failed because of child images
		. repeat ad nauseum?

"""

import sys
import docker
import time
import argparse

"""
# install deps on amazon-linux:
sudo yum install -y python27-pip.noarch
sudo pip-2.7 install docker-py
"""

def remove_images(image_list, num_attempts):
	""" take a list of either images or tags and, assuming the list
		isn't empty, attempt to delete them one by one -- remove successful
		ones from list """
	
	if not image_list: 
		print("Image list is empty!")
		return 

	attempt_count = 1
	while attempt_count <= num_attempts and len(image_list) > 0:
		print("Attempt number: %d" % attempt_count)
		successes = []
		for img in image_list:
			try:
				print("Deleting img tag %s" % img)
				#cli.remove_image(image=img)
			except Exception as e:
				print('Failed to remove image tag %s: %s' % (img,e))
			else:
				successes.append(img)
		[ image_list.remove(i) for i in successes ]
		attempt_count += 1


if __name__ == '__main__':

	cli = docker.Client(version='auto')

	parser = argparse.ArgumentParser(description='Delete old images and containers on Docker hosts')
	parser.add_argument('--preserve-running', 
						"-p", 
						default = False, 
						action = 'store_true',
						help="If true, preserve running containers and the images associated with them. Default is False"
					   )
	#parser.add_argument('--num-days', 
	#					'-n',
	#					default = 10,
	#					help= """ If --preserve-running is True, you can specify a minimum number of days old 
	#							an image or container must be before deleting it. Default is 10 """
	#				   )
	args = parser.parse_args()

	MAX_ATTEMPTS = 10

	# in case we just want to delete images older than certain threshold, ie 10 days:
	one_day = 86400
	#num_days = args.num_days
	num_days = 10
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

	# only exclude running containers on ecs host:	
	if args.preserve_running:
		print("Preserving running containers and associated images... ")
		del_container_ids = [ i for i in all_container_ids if i not in running_container_ids ]
		del_image_tags = [ i for i in all_image_tags if i not in used_image_tags ]
		del_image_ids = [ i for i in all_image_ids if i not in used_image_ids ]
	else:
		print("Attempting to delete ALL containers and images... ")
		del_container_ids = all_container_ids
		del_image_tags = [ i for i in all_image_tags ]
		del_image_ids = [ i for i in all_image_ids ]

		# notice this isn't using all_image_tags -- because we need the time info in the dict:
		#del_image_tags = { j for i in all_images for j in i['RepoTags'] if type(i['RepoTags']) == list and (unix_time - i['Created']) > time_threshold }
		# notice this isn't using all_image_ids -- because we need the time info in the dict:
		#del_image_ids = [ i['Id'] for i in all_images if (unix_time - i['Created']) > time_threshold ]


	# delete containers -- need to remove excludes from runtime params:
	for ct in del_container_ids:
		# set force=False just in case to prevent accidental container deletion, 
		# even though above logic should already have removed them from deletion list:
		FORCE = False if args.preserve_running else True
		try:
				print("Deleting container %s" % ct)
				#cli.remove_container(container=ct, force=FORCE)
		except Exception as e:
				print('Failed to remove container %s: %s' % (ct,e))	

	# remove images by tag first:
	remove_images(del_image_tags, MAX_ATTEMPTS)

	# then by ID:
	remove_images(del_image_ids, MAX_ATTEMPTS)


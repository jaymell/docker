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

"""
# install deps on amazon-linux:
sudo yum install -y python27-pip.noarch
sudo pip-2.7 install docker-py
"""

cli = docker.Client(version='auto')

# in case we just want to delete images older than certain threshold, ie 10 days:
one_day = 86400
num_days = 10
time_threshold = num_days * one_day
unix_time = time.time() 

running_containers = cli.containers(all=False)
running_container_ids = [ i['Id'] for i in running_containers ]
all_containers = cli.containers(all=True)
all_container_ids = [ i['Id'] for i in all_containers ]

ecs_host = True
build_host = False

# technically not ALL images, but good enough for now?
all_images = cli.images()
all_image_ids = { i['Id'] for i in all_images }
all_image_tags = { j for i in all_images for j in i['RepoTags'] if type(i['RepoTags']) == list }
used_image_ids = { i['ImageID'] for i in running_containers }
used_image_tags = { i['Image'] for i in running_containers }

# only exclude running containers on ecs host:	
if ecs_host:
	del_container_ids = [ i for i in all_container_ids if i not in running_container_ids ]
	del_image_ids = [ i for i in all_image_ids if i not in used_image_ids ]
elif build_host:
	del_container_ids = all_container_ids
	###
	# this is where we need jenkins magic:
	###
	#del_image_ids = [ i['Id'] for i in all_images if (unix_time - i['Created']) > time_threshold ]
	del_image_tags = [ i['Id'] for i in all_images if (unix_time - i['Created']) > time_threshold ]
else:
	print("What kind of host are you?")
	sys.exit(1)

# delete containers -- need to remove excludes from runtime params:
for ct in del_container_ids:
	try:
            print("Deleting container %s" % ct)
            #cli.remove_container(container=ct)
	except Exception as e:
            print('Failed to remove container %s: %s' % (ct,e))	

for img in del_image_ids:
    try: 
        print("Deleting img %s" % img)
        #cli.remove_image(image=img)
    except Exception as e:
        print('Failed to remove image %s: %s' % (img,e))


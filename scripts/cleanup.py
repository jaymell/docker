#!/usr/bin/python

"""
run-time parameters
	-- list of container IDs to exclude
	-- list of image IDs to exclude

. get _all_ containers
	if ecs host:
	. get images used by running containers
	. remove running containers from list
. remove any container excludes passed at runtime
. remove all containers left in list

. get _all_ images
	if build host:
		remove ones with certain tags -- get via jenkins request?
		remove ones less than certain age ? (probably only if jenkins doesn't work)
	if ecs host:
		remove ones associated with containers from list 

. remove any image excludes passed at runtime
. remove all images left in list

"""

import sys
import docker
import time

cli = docker.Client(version='auto')

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
all_images = cli.images(all=True)
all_image_ids = { i['Id'] for i in all_images }
used_image_ids = { i['ImageID'] for i in running_containers }

# only exclude running containers on ecs host:	
if ecs_host:
	del_container_ids = [ i for i in all_container_ids if i not in running_container_ids ]
	del_image_ids = [ i for i in all_image_ids if i not in used_image_ids ]
elif build_host:
	del_container_ids = all_container_ids
	###
	# this is where we need jenkins magic:
	###
	del_image_ids = [ i['Id'] for i in all_images if (unix_time - i['Created']) > time_threshold ]
else:
	print("What kind of host are you?")
	sys.exit(1)

# delete containers -- need to remove excludes from runtime params:
for ct in del_container_ids:
	try:
            print("Deleting container %s" % ct)
            cli.remove_container(container=ct)
	except Exception as e:
            print('Failed to remove container %s: %s' % (ct,e))	

for img in del_image_ids:
    try: 
        print("Deleting img %s" % img)
        cli.remove_image(image=img)
    except Exception as e:
        print('Failed to remove image %s: %s' % (img,e))

# way overcomplicated but fun:
#all_tags = { j for i in images for j in i['RepoTags'] if type(i['RepoTags']) == list }

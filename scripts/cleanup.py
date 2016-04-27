import docker

cli = docker.Client(version='auto')
images = cli.images()

# comprehension:
all_tags = [ j for i in images for j in i['RepoTags'] if type(i['RepoTags']) == list ]

# busted out into loops:
all_tags = []
for i in images:
    if 'RepoTags' in i and type(i['RepoTags']) == list:
        for j in i['RepoTags']:
            all_tags.append(j)

########################################################

running_containers = cli.containers()
images = cli.images()
image_ids = { i['Id'] for i in images }
container_image_ids = { i['ImageID'] for i in running_containers }

""" 
currently not working that well...
steps:
    get list of ALL containers, 
    then filter that down to only STOPPED containers by removing IDs of RUNNING containers
    then delete those containers
    then do the following
    then figure out how to deal with the dependent child images
"""

for i in image_ids:
    if i not in container_image_ids:
        try:
            cli.remove_image(image=i)
        except Exception as e:
            print(e)

        
[ cli.remove_image(image=i) for i in image_ids if i not in container_image_ids ]


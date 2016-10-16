from collections import namedtuple

ClusterConfig = namedtuple('ClusterConfig', ['username', 'email', 'group_list'])

myClusterConfig = ClusterConfig(
  username = 'adarsh',
  email = 'adarsh@email.arizona.edu',
  group_list = 'shufang',
)

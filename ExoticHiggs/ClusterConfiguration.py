class ClusterConfiguration(object):
    def __init__(self, username, email, group_list):
        self.username = username
        self.email = email
        self.group_list = group_list

myClusterConfig = ClusterConfiguration(
  username = 'adarsh',
  email = 'adarsh@email.arizona.edu',
  group_list = 'shufang',
)

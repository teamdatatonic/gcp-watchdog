# ----------------------------------------------------------------------
# Copyright (c) 2016 Datatonic
# ----------------------------------------------------------------------

"""
This contains calls through the gcloud compute and ressourcemanager API

"""

from gcloud import resource_manager

def get_projects(credentials=None):
    """
    Get list of all projects on GCP the service account has access to
    """

    data = []
    client = resource_manager.Client(credentials=credentials)
    projects = list(client.list_projects())
    data = map(lambda x: [str(x.name), str(x.project_id)], projects)

    return data

def get_gcp_zones(compute, project):
    """
    Get all zones in GCP (needs compute engine)
    """

    zones = []
    details = compute.zones().list(project=str(project)).execute()
    if details.has_key('items'):
        for item in details['items']:
            zones.append(str(item['name']))

    return zones

def get_instance_data(compute, project_IDs, zones):
    """
    Get info on instances (needs compute engine)
    """

    data = []
    #loop over all projects
    for project in project_IDs:
        #loop over all zones
        for zone in zones:
            response = compute.instances().list(project=str(project), zone=zone).execute()
            if response.has_key('items'):
                for item in response['items']:
                    data.append([str(item['name']), str(item['status']),
                                 str(item['machineType']).split('/')[-1], str(project), zone])

    return data

def get_firewall_data(compute, project_IDs):
    """
    Get firwall rules (needs compute engine)
    """
    data = []
    #loop over all projects
    for project in project_IDs:
        response = compute.firewalls().list(project=str(project)).execute()

        if response.has_key('items'):
            for item in response['items']:
                if item.has_key('allowed'):
                    for allowed in item['allowed']:
                        data.append([str(project), str(item['name']),
                                     str(item['sourceRanges'][0]) if item.has_key('sourceRanges') else '', 
                                     str(allowed['IPProtocol']),
                                     allowed['ports'][0] if allowed.has_key('ports')
                                     else None, str(item['kind'])])

    return data

def get_people_access(project_rm, project_IDs):
    """
    Get access rights of users (needs ressource manager)
    """

    data = []
    #loop over all projects
    for project in project_IDs:
        response = project_rm.projects().getIamPolicy(body={}, resource=str(project)).execute()

        if response.has_key('bindings'):
            for binding in response['bindings']:

                if binding.has_key('role'):
                    role = binding['role']

                if binding.has_key('members'):
                    for member in binding['members']:

                        account_type = str(member).split(':')[0]
                        email = str(member).split(':')[1]

                        data.append([str(project), str(email.split('@')[0]).replace('.', ' '),
                                     email, email.rsplit('@')[1], account_type, str(role)[6:]])
    return data













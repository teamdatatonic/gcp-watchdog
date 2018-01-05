# ----------------------------------------------------------------------
# Copyright (c) 2016 Datatonic
# ----------------------------------------------------------------------

"""
Applies the rules of the watchdog.yaml to the GCP data

notify-rules: white-list
ignore-rules: black-list
alert-rules : color highlight

"""

import pandas as pd
from googleapiclient.errors import HttpError

# Colors for highlighting
color_string = 'background-color: darkorange'
default_color_string = 'background-color: '

def check_projects(compute, rm, projects):
    """
    Checks if compute, ressource manager and permissions are correct
    If permissions are not met, the project is excluded

    Add unaccessible projects and the reason to a dataframe(to be displayed in report)
    """

    inaccessible_projects = []
    inaccessible_reasons = []

    for project in projects['Project_ID'].tolist():
        try:
            compute.zones().list(project=str(project)).execute()

        except HttpError:
            print("\nGCP Error: Compute Engine is not configured for %s \nor "
                  "the service account does not have perimssions to access it" % project)

            inaccessible_projects.append(str(project))
            inaccessible_reasons.append("GCE or SA")

            projects = projects[projects.Project_ID != project]
            continue

        try:
            rm.projects().getIamPolicy(body={}, resource=str(project)).execute()

        except HttpError:
            print("GCP Error: Ressource Manager is not configured for %s \nor "
                  "the service account does not have perimssions to access it" % project)
            
            inaccessible_projects.append(str(project))
            inaccessible_reasons.append("RM")

            projects = projects[projects.Project_ID != project]
            continue

    inaccessible_projects_df = pd.DataFrame({'Project_ID': inaccessible_projects,
        'Reason': inaccessible_reasons})

    return projects, inaccessible_projects_df

def alert_projects(projects, general_cfg):
    """
    Return filtered projects
    """

    rules_list = ['ignore-projects', 'notify-projects']
    alert_instances_list = ['name', 'poject-ID']
    columns_dict = {'name': 'Name', 'poject-ID': 'Project_ID'}

    for rule in rules_list:

        for alert in alert_instances_list:
            if alert in general_cfg[rule].keys():

                if type(general_cfg[rule][alert]) == list:
                    string = [d['string'] for d in general_cfg[rule][alert] if 'string' in d]
                else:
                    string = [general_cfg[rule][alert]]

                if string[0] != None:

                    if rule == 'ignore-projects':
                        projects = projects.loc[- projects[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'notify-projects':
                        projects = projects.loc[projects[columns_dict[alert]]\
                        .str.contains('|'.join(string))]

    projects.reset_index(inplace=True)
    projects.drop('index', axis=1, inplace=True)
    projects.index += 1
    return projects

def alert_zones(zones, general_cfg):
    """
    Return filtered zones
    """

    rules_list = ['ignore-zones', 'notify-zones']
    alert_instances_list = ['name']
    columns_dict = {'name': 'Name'}

    for rule in rules_list:

        for alert in alert_instances_list:
            if alert in general_cfg[rule].keys():

                if type(general_cfg[rule][alert]) == list:

                    string = [d['string'] for d in general_cfg[rule][alert] if 'string' in d]
                else:
                    string = [general_cfg[rule][alert]]

                if string[0] != None:

                    if   rule == 'ignore-zones':
                        zones = zones.loc[- zones[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'notify-zones':
                        zones = zones.loc[zones[columns_dict[alert]]\
                        .str.contains('|'.join(string))]

    zones.reset_index(inplace=True)
    zones = zones.drop('index', axis=1)
    zones.index += 1
    return zones

def alert_instances(instances, alert_cfg):
    """
    Return filtered instances of all projects
    """

    rules_list = ['ignore-rules', 'notify-rules', 'alert-rules']
    alert_instances_list = ['status', 'machine-type', 'name']
    columns_dict = {'status': 'Status', 'machine-type': 'Machine_type', 'name': 'Instance'}
    highlight_index = []

    for rule in rules_list:
        # Prepare for alert highlighting
        if rule == 'alert-rules':
            instances.reset_index(inplace=True)
            instances = instances.drop('index', axis=1)
            instances.index += 1

        for alert in alert_instances_list:
            if alert in alert_cfg[rule].keys():

                if type(alert_cfg[rule][alert]) == list:
                    string = [d['string'] for d in alert_cfg[rule][alert] if 'string' in d]
                else:
                    string = [alert_cfg[rule][alert]]

                if string[0] != None:

                    if   rule == 'ignore-rules':
                        instances = instances.loc[- instances[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'notify-rules':
                        instances = instances.loc[instances[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'alert-rules':
                        highlight_index.extend(instances[instances[columns_dict[alert]]\
                            .str.contains('|'.join(string))].index.tolist())

    colors = [color_string for i in range(instances.shape[1])]
    default_colors = [default_color_string for i in range(instances.shape[1])]

    instances_styler = instances.style
    if instances.shape[0] > 0:
        instances_styler = instances_styler.apply(
            lambda x: colors if (x.name in set(highlight_index)) else default_colors, axis=1)

    instances_styler.set_table_attributes("border=1")
    return instances, instances_styler

def alert_iam(iam, alert_cfg):
    """
    Returns filtered persona and accounts
    """

    rules_list = ['ignore-rules', 'notify-rules', 'alert-rules']
    alert_instances_list = ['name', 'email', 'account-type', 'role']
    columns_dict = {'name': 'Name', 'email': 'Email',
                    'account-type': 'Account_type', 'role': 'Role'}
    highlight_index = []

    for rule in rules_list:
        # Prepare for alert highlighting
        if rule == 'alert-rules':
            iam.reset_index(inplace=True)
            iam = iam.drop('index', axis=1)
            iam.index += 1

        for alert in alert_instances_list:
            if alert in alert_cfg[rule].keys():

                if type(alert_cfg[rule][alert]) == list:
                    string = [d['string'] for d in alert_cfg[rule][alert] if 'string' in d]
                else:
                    string = [alert_cfg[rule][alert]]

                if string[0] != None:

                    if   rule == 'ignore-rules':
                        iam = iam.loc[- iam[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'notify-rules':
                        iam = iam.loc[iam[columns_dict[alert]].\
                        str.contains('|'.join(string))]
                    elif rule == 'alert-rules':
                        highlight_index.extend(iam[iam[columns_dict[alert]]\
                            .str.contains('|'.join(string))].index.tolist())

    colors = [color_string for i in range(iam.shape[1])]
    default_colors = [default_color_string for i in range(iam.shape[1])]

    iam_styler = iam.style
    if iam.shape[0] > 0:
        iam_styler = iam_styler.apply(
            lambda x: colors if (x.name in set(highlight_index)) else default_colors, axis=1)

    iam_styler.set_table_attributes("border=1")
    return iam, iam_styler

def alert_firewalls(firewalls, alert_cfg):
    """
    Returns filtered firewall
    """
    rules_list = ['ignore-rules', 'notify-rules', 'alert-rules']
    alert_instances_list = ['name', 'range', 'protocol', 'port']
    columns_dict = {'name': 'Rule_name', 'range': 'Range',
                    'protocol': 'Protocol', 'port': 'Port'}
    highlight_index = []

    for rule in rules_list:
        # Prepare for alert highlighting
        if rule == 'alert-rules':
            firewalls.reset_index(inplace=True)
            firewalls = firewalls.drop('index', axis=1)
            firewalls = firewalls.drop('Firewall_type', axis=1)
            firewalls.index += 1

        for alert in alert_instances_list:
            if alert in alert_cfg[rule].keys():

                if type(alert_cfg[rule][alert]) == list:
                    string = [d['string'] for d in alert_cfg[rule][alert] if 'string' in d]
                else:
                    string = [alert_cfg[rule][alert]]

                if string[0] != None:

                    if   rule == 'ignore-rules':
                        firewalls = firewalls.loc[- firewalls[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'notify-rules':
                        firewalls = firewalls.loc[firewalls[columns_dict[alert]]\
                        .str.contains('|'.join(string))]
                    elif rule == 'alert-rules':
                        highlight_index.extend(firewalls[firewalls[columns_dict[alert]]\
                        .str.contains('|'.join(string))].index.tolist())

    colors = [color_string for i in range(firewalls.shape[1])]
    default_colors = [default_color_string for i in range(firewalls.shape[1])]

    firewalls_styler = firewalls.style
    if firewalls.shape[0] > 0:
        firewalls_styler = firewalls_styler.apply(
            lambda x: colors if (x.name in set(highlight_index)) else default_colors, axis=1)

    firewalls_styler.set_table_attributes("border=1")
    return firewalls, firewalls_styler
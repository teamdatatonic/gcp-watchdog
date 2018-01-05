# ----------------------------------------------------------------------
# Copyright (c) 2016 Datatonic
# ----------------------------------------------------------------------

"""
Google Cloud Platform (GCP) watchdog (unofficial)

Main Script which creates a report based on the configuration file (watchdog.yaml)

"""

import datetime
import os
import argparse
import yaml
import pkg_resources
import pandas as pd

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from jinja2 import Environment, FileSystemLoader

from security.gcp_calls import get_projects, get_gcp_zones, get_instance_data
from security.gcp_calls import get_firewall_data, get_people_access
from security.alerts import check_projects, alert_projects, alert_zones
from security.alerts import alert_instances, alert_firewalls, alert_iam

from send_email import send_email

def main():
    """
    Main function
    """

    # Parse Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c',
                        dest='config_file',
                        default="watchdog.yaml",
                        help='Configuration file (required)')
    parser.add_argument('--email',
                        dest='email',
                        action='store_true',
                        help='send report as email')
    parser.add_argument('--output', '-o',
                        dest='report_file',
                        default="report.html",
                        help='Set output file name (default: report.html)')
    parser.add_argument('--no-output', '-n',
                        dest='no_output',
                        action='store_true',
                        help="Don't output report file")

    args = parser.parse_args()

    # Parse watchdog configuration file (watchdog.yaml)
    with open(args.config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)


    # Print header
    print "\n***** Google Cloud Platform Watchdog *****\n"
    print 'Report Title:', cfg['general']['report-title']
    print "Watchdog email: ", cfg['general']['watchdog-email']
    print "Receivers: "
    for email in cfg['general']['receiver-email']:
        print "Email: ", email['email']

    print "\nRequested reports: \n"
    if cfg['compute']['print']:
        print '- compute'
    if cfg['IAM']['print']:
        print '- IAM'
    if cfg['firewall']['print']:
        print '- firewall'

    # Get authentication and GCP APIs
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

    compute = discovery.build('compute', 'v1', credentials=credentials)
    rm = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)


    # Get data and alerts from GCP
    tables = []
    table_titles = []

    # Get projects
    projects_columns = ['Name', 'Project_ID']
    projects_data = get_projects(credentials)
    projects = pd.DataFrame(projects_data, columns=projects_columns)
    projects, inaccessible_projects = check_projects(compute, rm, projects)

    print(projects)
    projects = alert_projects(projects, cfg['general'])
    project_IDs = projects['Project_ID'].tolist()

    # Render table of unaccessible projects
    print(inaccessible_projects.head(20))
    colors = ['background-color: darkorange' for i in range(inaccessible_projects.shape[1])]
    inaccessible_projects_styler = inaccessible_projects.style
    if inaccessible_projects.shape[0] > 0:
        inaccessible_projects_styler = inaccessible_projects_styler.apply(
            lambda x: colors, axis=1)

    inaccessible_projects_styler.set_table_attributes("border=1")
    tables.append(inaccessible_projects_styler.render())
    table_titles.append('Incaccessible Projects')

    # Get zones
    zone_columns = ['Name']
    zones_data = get_gcp_zones(compute, project_IDs[0])
    zones = pd.DataFrame(zones_data, columns=zone_columns)
    zones = alert_zones(zones, cfg['general'])
    zones = zones['Name'].tolist()

    if cfg['compute']['print']:
        instances_coulmns = ['Instance', 'Status', 'Machine_type', 'Project_ID', 'Zone']

        instance_data = get_instance_data(compute, project_IDs, zones)
        instances = pd.DataFrame(instance_data, columns=instances_coulmns)

        # Get alerts and filters
        instances, alerted_instances_styler = alert_instances(instances, cfg['compute'])

        tables.append(alerted_instances_styler.render())
        table_titles.append('Instances')


    if cfg['IAM']['print']:
        iam_coulmns = ['Project_ID', 'Name', 'Email', 'Email_suffix', 'Account_type', 'Role',]

        iam_data = get_people_access(rm, project_IDs)
        iam = pd.DataFrame(iam_data, columns=iam_coulmns)
        iam = iam.groupby(['Project_ID', 'Name', 'Email', 'Email_suffix', 'Account_type'])['Role']\
        .apply(list).reset_index()

        # Get alerts and filters
        alerted_iam, alerted_iam_styler = alert_iam(iam, cfg['IAM'])

        tables.append(alerted_iam_styler.render())
        table_titles.append('IAM')


    if cfg['firewall']['print']:
        firewalls_columns = ['Project_ID', 'Rule_name', 'Range',
                             'Protocol', 'Port', 'Firewall_type']

        firewall_data = get_firewall_data(compute, project_IDs)
        firewalls = pd.DataFrame(firewall_data, columns=firewalls_columns)

        # Get alerts and filters
        alerted_firewalls, alerted_firewalls_styler = alert_firewalls(firewalls, cfg['firewall'])

        tables.append(alerted_firewalls_styler.render())
        table_titles.append('Firewalls')


    # Create report

    # Construct email content
    templates_folder = pkg_resources.resource_filename('templates','')
    env = Environment(loader=FileSystemLoader(templates_folder))
    content = {'title': cfg['general']['report-title'] + '  ' + str(datetime.datetime.now())[:-7],
               'num_tables': len(tables),
               'table_titles': table_titles,
               'tables' : tables
              }
    # Render HTML
    html = env.get_template('daily_report.html').render(content)
    subject = cfg['general']['report-title']


    # Write report to file
    if not args.no_output:
        report_file_path = args.report_file
        with open(report_file_path, 'w') as the_file:
            the_file.write(html)

    # Send email (needs email client to be configured)
    if args.email:
        for to_email in cfg['general']['receiver-email']:
            send_email(html, cfg['general']['watchdog-email'], to_email['email'], subject)


if __name__ == "__main__":
    main()

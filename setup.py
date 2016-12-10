from setuptools import setup, find_packages

setup(name='gcp-watchdog',
      version='0.1',
      description='Watchdog that monitors Google Cloud Platform services',
      long_description="""Watchdog that monitors Google Cloud Platform services. Creates a HTML report file which lists
                          compute instances, IAM (Identity and Access Management) and firewall rules""",
      url='http://github.com/teamdatatonic/gcp-watchdog',
      author='Oliver Gindele',
      author_email='oliver.gindele@datatonic.com',
      license='MIT',
      entry_points={
    'console_scripts': [
        'gcp-watchdog=watchdog.watchdog:main',]},
      install_requires=[
          'numpy',
          'pandas',
          'jinja2',
          'pyyaml',
          'google-api-python-client',
          'gcloud',
          'oauth2client',
          'inlinestyler',
          'sendgrid'
      ],
      package_data={'templates': ['layout.html', 'daily_report.html', 'watchdog_example.yaml']},
      include_package_data=True,
      packages=setuptools.find_packages()
      )

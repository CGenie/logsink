from setuptools import setup

setup(
    name='logsink_server',
    packages=['logsink_server'],
    include_package_data=True,
    install_requires=[
        'requests==2.12.4',
        'flask==0.12',
        'flask-restful==0.3.5',
        'flask-restful-swagger-2==0.32',
        'flask-cors==3.0.2',
        'influxdb==4.0.0',
        'python-dateutil==2.6.0',
        'pytz==2016.10',
    ]
)

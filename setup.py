from setuptools import setup

setup(
    name='pyUBX',
    version='0.1a',
    packages=['ubx', 'ubx.UBX'],
    url='https://github.com/mayeranalytics/pyUBX',
    license='GPL-3.0',
    author='Markus Mayer',
    author_email='info@mayeranalytics.com',
    description='Lightweight wrapper for uBlox GPS binary format (UBX)',
    install_requires = ['pyserial'],
    entry_points = {'console_scripts': [
        'UBXtool=ubx:UBXtool.ubxtool_main',
        'parse_NMEA_log=ubx:parse_NMEA_log.parse_NMEA_log_main'
    ]}
)

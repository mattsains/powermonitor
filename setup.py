from distutils.core import setup, Extension

setup(
    name='powermonitor',
    version='0.1a',
    packages=['Events', 'Database', 'Reporting', 'DataAnalysis', 'DataAnalysis.Exceptions', 'GPIOInterface'],
    url='https://github.com/mattsains/powermonitor',
    license='GPL',
    author='EcoBerry',
    author_email='powermonitor.ecoberry@gmail.com',
    description='Intelligent Household Power Monitor',
    # ext_modules=[Extension('', [''])],  # Any c extensions that must be included
    install_requires=['apscheduler', 'beautifulsoup4', 'django', 'matplotlib', 'numpy', 'pandas', 'pymysql', 'patsy',
              'premailer', 'python-dateutil', 'pytz', 'scipy', 'spidev', 'sqlalchemy', 'statsmodels']
)
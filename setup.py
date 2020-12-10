from setuptools import setup
from setuptools import find_packages
import versioneer

# README #
def readme():
    with open('README.md') as f:
        return f.read()

setup(name='purple_haze',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python package to merging Purple Air air quality data with City of Seattle SES data',
      long_description=readme(),
      keywords='air quality socio-economic comparison',
      url='https://github.com/adambsokol/purple_haze',
      author='Adam Sokol, Tyler Cox, Carley Frederickson, Greta Shum',
      license='MIT',
      packages=find_packages(exclude=['tests*','docs*']),
      package_data={'': ['*.csv']},
      include_package_data=True,
      install_requires=[
          'altair=4.1.0',
          'descartes=1.1.0',
          'geopandas=0.6.1',
          'geopandas=0.6.1',
          'ipykernel=5.3.4',
          'ipython=7.19.0',
          'ipython_genutils=0.2.0',
          'ipywidgets=7.5.1',
          'jupyter_client=6.1.7',
          'jupyter_core=4.7.0',
          'jupyterlab=2.2.6',
          'jupyterlab_pygments=0.1.2',
          'jupyterlab_server=1.2.0',
          'nodejs=10.13.0',
          'notebook=6.1.4',
          'numpy<=1.18',
          'pandas=1.1.3',
          'python=3.8.2',
          'python-dateutil=2.8.1',
          'scipy=1.5.2',
          'shapely=1.6.4',
          'voila=0.2.4',
          'xarray=0.16.1',
      ],
      zip_safe=False,
      # extras_require={'docs': ['sphinx>=1.4', 'nbsphinx'],
      #                 'dev' : ['notebook', 'wheel', 'twine'],
      #                 'test': ['pytest>=4.0', 'nbval', 'pytest-cov', 'codecov']}
)


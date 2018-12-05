from setuptools import setup, find_packages

setup(name='ib_orchestrator_api',
      version='0.2.5',
      description='Bayware Northbound API Library',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Network',
      ],
      url='https://github.com/Bayware/ib-orchestrator-api',
      author='Bayware',
      packages=find_packages(),
      install_requires=[
          'requests>=2.19.1',
          'urllib3>=1.23'
      ],
      include_package_data=True,
      zip_safe=False)

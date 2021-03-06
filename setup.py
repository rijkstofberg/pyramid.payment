import os

from setuptools import setup, find_packages

version='0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()
LICENSE = open(os.path.join(here, 'LICENSE.md')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'deform',
    'paymentintegrations',
    ]

setup(name='pyramid.payment',
      version=version,
      description='pyramid.payment',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Rijk Stofberg',
      author_email='rijk.stofberg@gmail.com',
      url='',
      license=LICENSE,
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyramidpayment',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pyramidpayment:main
      [console_scripts]
      initialize_pyramid.payment_db = pyramidpayment.scripts.initializedb:main
      add_demo_data = pyramidpayment.scripts.add_demo_data:main
      """,
      )

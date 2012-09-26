import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='odontux',
      version='0.0',
      description='odontux',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Franck LABADILLE',
      author_email='franck@labadille.net',
      url='labadille.net',
      keywords='odontux odontology dental',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='odontux',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = odontux:main
      [console_scripts]
      initialize_odontux_db = odontux.scripts.initializedb:main
      """,
      )


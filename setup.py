import os
from setuptools import setup
from adminpp import VERSION

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='adminpp',
    version='.'.join(str(x) for x in VERSION),
    packages=['adminpp'],
    description='A helper module to implement django-admin features nicely.',
    long_description=README,
    author='Won-guk Jung',
    author_email='chank1012@naver.com',
    url='https://github.com/mathpresso/adminpp/',
    license='MIT',
    install_requires=[
        'Django>=1.8',
        'six>=1.10.0',
    ],
    classifiers=[
        'Framework :: Django',
    ],
)

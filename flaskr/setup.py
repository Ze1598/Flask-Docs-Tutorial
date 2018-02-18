from setuptools import setup

setup(
    name='flaskr',
    packages=['flaskr'],
    include_package_data=True,
    install_requires=['flask',],
    setup_requires = ['pytest-runner',],
    test_require = ['pytest',],
)
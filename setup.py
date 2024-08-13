from setuptools import setup, find_packages

setup(
    name='trackinglog',
    version='0.1.1',
    description='A logging package for tracing function calls with error handling and email notification',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Yinghao Li',
    author_email='shiyi.yinghao@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.11',
)


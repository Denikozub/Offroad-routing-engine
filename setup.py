from setuptools import setup, find_packages


REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
if __name__ == "__main__":
    setup(
        packages=find_packages(
            where='src',
            include=['offroad_routing'],
        ),
        name='offroad_routing',
        version='0.2.0',
        description='Off-road navigation system.',
        author='Denis Kozub',
        author_email='denikozub@gmail.com',
        project_urls={
            'Documentation': 'https://denikozub.github.io/Offroad-routing-engine/',
            'Source': 'https://github.com/Denikozub/Offroad-routing-engine/'
        },
        install_requires=REQUIREMENTS,
        python_requires='>=3.8'
    )

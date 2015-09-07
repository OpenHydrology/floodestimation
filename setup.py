from setuptools import setup
import versioneer


setup(
    name='floodestimation',
    packages=['floodestimation'],
    package_data={
        'floodestimation': ['fehdata.json',
                            'config.ini'],
    },
    zip_safe=False,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass()
)

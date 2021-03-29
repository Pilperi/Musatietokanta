import setuptools

setuptools.setup(
    name="musatietokanta",
    version="2021.03.29",
    url="https://github.com/Pilperi/Musatietokanta",
    author="Pilperi",
    description="Työkalut musatietokantojen kanssa leikkimiseen",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires = [
        'tiedostohallinta @ git+https://github.com/Pilperi/Tiedostohallinta',
		"PyQt5"
    ],
	python_requires=">=3.8, <4",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
	include_package_data=True,
    package_data={'': ['./lataa_ja_lisaa.sh']}
)

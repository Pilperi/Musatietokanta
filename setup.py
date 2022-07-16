import setuptools
import os

setuptools.setup(
    name="musatietokanta",
    version="v2022.07.16",
    url="https://github.com/Pilperi/Musatietokanta",
    author="Pilperi",
    description="Työkalut musatietokantojen kanssa leikkimiseen",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires = [
        'tiedostohallinta @ git+https://github.com/Pilperi/Tiedostohallinta@v2022.04.18',
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

# Kirjoita alias bashrc:hen
KOTIKANSIO = os.path.expanduser("~")
bashtiedosto = os.path.join(KOTIKANSIO, ".bashrc")
bashrivi = f"alias musatietokanta=\'python -m musatietokanta.main\'\n"
# Katso ettei aliasta ole jo määritetty
kirjoitetaan = True
if os.path.exists(bashtiedosto):
	with open(bashtiedosto, "r") as bf:
		rivi = bf.readline()
		while rivi:
			if rivi == bashrivi:
				kirjoitetaan = False
				break
			rivi = bf.readline()
if kirjoitetaan:
	print(f"{bashrivi} >> {bashtiedosto}")
	bf = open(bashtiedosto, "a+")
	bf.write(bashrivi)
	bf.close()

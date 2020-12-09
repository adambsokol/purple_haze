from setuptools import setup, find_packages

opts = dict(
    name="Purple Haze",
    version="0.1",
    url="https://github.com/adambsokol/purple_haze",
    license="MIT",
    author="Tyler Cox, Carley Fredrickson, Greta Shum, Adam Sokol",
    description="Tool for merging air quality and socioeconomic data",
    packages=find_packages()
    )

if __name__ == "__main__":
    setup(**opts)

import setuptools


setuptools.setup(
    name="datasmoothie-tally-client",
    packages=setuptools.find_packages(),
    extras_require={':python_version>"3.0"': ['importlib-resources']},
    version="0.1",
    license='MIT',
    include_package_data=True,
    url="https://github.com/datasmoothie/datasmoothie-tally-client",
    #download_url="https://github.com/datasmoothie/datasmoothie-tally-client/archive/v0.0.1.tar.gz",
    author="Geir Freysson",
    author_email="geir@datasmoothie.com",
    description="Python wrapper for the Tally API.",
    keywords=['surveys', 'market research', 'weighting', 'significance tests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

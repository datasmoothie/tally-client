import setuptools


setuptools.setup(
    name="datasmoothie-tally-client",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'pandas',
    ],
    version="0.15",
    license='MIT',
    include_package_data=True,
    url="https://github.com/datasmoothie/datasmoothie-tally-client",
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

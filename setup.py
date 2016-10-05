try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='rigexpert-tool',
    version='1.0.0',
    description='CLI tool to dump, plot, or convert RigExpert Antenna Analyzer impedance sweeps',
    author='vsergeev',
    author_email='v@sergeev.io',
    url='https://github.com/vsergeev/rigexpert-tool',
    py_modules=['rigexpert_tool'],
    install_requires=['pyserial', 'matplotlib', 'scipy'],
    entry_points={
        'console_scripts': [
            'rigexpert-tool=rigexpert_tool:main',
        ],
    },
    long_description="rigexpert-tool is a CLI tool to dump, plot, and convert impedance sweeps from a `RigExpert <http://www.rigexpert.com/>`_ antenna analyzer. The sweeps are stored in CSV. See https://github.com/vsergeev/rigexpert-tool for examples and more information.",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering",
        "Topic :: Communications :: Ham Radio",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    license='MIT',
    keywords='rigexpert vswr swr antenna analyzer',
)

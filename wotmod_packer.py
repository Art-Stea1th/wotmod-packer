from compileall import compile_dir
from itertools import chain
from os import rename, walk, remove, makedirs
from os.path import join, abspath, dirname, splitext, split, exists, normpath
from re import IGNORECASE, search
from shutil import copytree, make_archive, rmtree, register_archive_format
from tempfile import gettempdir
from uuid import uuid4
from xml.etree.ElementTree import parse
from zipfile import ZipFile, ZIP_STORED

GAME_PATH = r'D:\Games\World of Tanks'
BUILD_OUTPUT = '.'

_MOD_EXT = 'wotmod'


class TempDirectory(object):
    def __init__(self):
        self.__root = gettempdir()
        self.__pref = 'mod_build_'
        self.__path = None
        self.__removeTempDirectories('^{}{}'.format(self.__pref, r'(\d|\w){8}-((\d|\w){4}-){3}(\d|\w){12}$'))

    def __enter__(self):
        self.__path = join(self.__root, '{}{}'.format(self.__pref, (str(uuid4()))))
        makedirs(self.__path)
        return self.__path

    def __exit__(self, tp, vl, tb):
        rmtree(self.__path)

    def __removeTempDirectories(self, pattern):
        _, dirNames, _ = walk(self.__root).next()
        for dirName in dirNames:
            if search(pattern, dirName, IGNORECASE):
                rmtree(join(self.__root, dirName))


def packMod():
    sourcesRoot, modName = _getModInfo()
    destinationFolder = (
        _getGameModsFolder(GAME_PATH) if exists(join(GAME_PATH, 'WorldOfTanks.exe'))
        else BUILD_OUTPUT if exists(BUILD_OUTPUT) else '.'
    )
    with TempDirectory() as tempDirectory:
        _compileTree(
            sourcesRoot,
            join(tempDirectory, r'res\scripts\client\gui\mods')
        )
        _packTree(
            tempDirectory,
            join(destinationFolder, '{}.{}'.format(modName, _MOD_EXT))
        )


def _getModInfo():
    path = dirname(abspath(__file__))
    for entry in _walkWithCriteria(path, lambda e: search(r'^mod_.*\.py$', e, IGNORECASE)):
        dirName, fileName = split(entry)
        return dirName, splitext(fileName)[0]
    return None, None


def _compileTree(source, target):
    copytree(source, target)
    compile_dir(target, maxlevels=128, quiet=True)
    for fsEntry in _walkWithCriteria(target, lambda e: splitext(e)[1] == '.py'):
        remove(fsEntry)


def _packTree(source, target):
    if exists(target):
        remove(target)
    register_archive_format(_MOD_EXT, _makeWotModFile, description='WoT Modification')
    rename(make_archive(str(uuid4()), _MOD_EXT, source), target)


def _makeWotModFile(name, baseDir, **_):
    modFilename = '{}.{}'.format(name, _MOD_EXT)
    with ZipFile(modFilename, 'w', ZIP_STORED) as modFile:
        for entry in _walkWithCriteria(baseDir):
            modFile.write(entry, entry)
    return modFilename


def _getGameModsFolder(gameRoot):
    return join(gameRoot, 'mods', _getGameVersion(gameRoot))


def _getGameVersion(gameRoot):
    vNode = parse(join(gameRoot, 'version.xml')).getroot().find('version')
    vMatch = search(r'v\.((\d\.)+\d)+', vNode.text, IGNORECASE)
    return vMatch.group(1)


def _walkWithCriteria(path, entryCriteria=None):
    for dirPath, dirNames, fileNames in walk(path):
        for entry in chain(dirNames or (), fileNames or ()):
            if not entryCriteria or entryCriteria(entry):
                yield normpath(join(dirPath, entry))


if __name__ == '__main__':
    packMod()

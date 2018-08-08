# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2015 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================
"""Constants and classes to define for each new game - still a WIP."""

from .. import brec
# from .constants import * # TODO(ut): create a .constants module

class GameInfo(object):
    # Main game info - should be overridden -----------------------------------
    # Name of the game to use in UI.
    displayName = u'' ## Example: u'Skyrim'
    # Name of the game's filesystem folder.
    fsName = u'' ## Example: u'Skyrim'
    # Alternate display name of Wrye Bash when managing this game
    altName = u'' ## Example: u'Wrye Smash'
    # Name of game's default ini file.
    defaultIniFile = u''
    # Exe to look for to see if this is the right game
    exe = u'' ## Example: u'TESV.exe'
    # The main plugin Wrye Bash should look for
    masterFiles = []
    # INI files that should show up in the INI Edits tab
    #  Example: [u'Oblivion.ini']
    iniFiles = []
    # The pickle file for this game.  Holds encoded GMST IDs from the big list below
    pklfile = ur'bash\db\*GAMENAME*_ids.pkl'
    # Registry keys to read to find the install location
    # These are relative to:
    #  HKLM\Software
    #  HKLM\Software\Wow6432Node
    #  HKCU\Software
    #  HKCU\Software\Wow6432Node
    # Example: (u'Bethesda Softworks\\Oblivion', u'Installed Path')
    regInstallKeys = ()
    # URL to the Nexus site for this game
    nexusUrl = u''   # URL
    nexusName = u''  # Long Name
    nexusKey = u''   # Key for the "always ask this question" setting in settings.dat

    # Additional game info - override as needed -------------------------------
    # URL to download patches for the main game.
    patchURL = u''
    # Tooltip to display over the URL when displayed
    patchTip = u'Update via Steam'
    # Bsa info
    allow_reset_bsa_timestamps = False
    bsa_extension = ur'bsa'
    supports_mod_inis = True  # this game supports mod ini files aka ini fragments
    vanilla_string_bsas = {}
    resource_archives_keys = ()
    # plugin extensions
    espm_extensions = {u'.esp', u'.esm'}
    # Load order info
    using_txt_file = True
    # bethesda net export files
    has_achlist = False

    def __init__(self, gamePath):
        self.gamePath = gamePath # absolute bolt Path to the game directory

    # Construction Set information
    class cs(object):
        imageName = u''   # Image name template for the status bar
        longName = u''    # Full name
        exe = u'*DNE*'    # Executable to run
        shortName = u''   # Abbreviated name
        seArgs = u''      # Argument to pass to the SE to load the CS

    # Script Extender information
    class se(object):
        shortName = u''   # Abbreviated name.  If this is empty, it signals that no SE is available
        longName = u''    # Full name
        exe = u''         # Exe to run
        steamExe = u''    # Exe to run if a steam install
        url = u''         # URL to download from
        urlTip = u''      # Tooltip for mouse over the URL

    # Script Dragon
    class sd(object):
        shortName = u''
        longName = u''
        installDir = u''

    # SkyProc Patchers
    class sp(object):
        shortName = u''
        longName = u''
        installDir = u''

    # Quick shortcut for combining the SE and SD names
    @classmethod
    def se_sd(cls):
        se_sd_ = cls.se.shortName
        if cls.sd.longName: se_sd_ += u'/' + cls.sd.longName
        return se_sd_

    # Graphics Extender information
    class ge(object):
        shortName = u''
        longName = u''
        # exe is treated specially here.  If it is a string, then it should
        # be the path relative to the root directory of the game, if it is
        # a list, each list element should be an iterable to pass to Path.join
        # relative to the root directory of the game.  In this case,
        # each filename will be tested in reverse order.  This was required
        # for Oblivion, as the newer OBGE has a different filename than the
        # older OBGE
        exe = u''
        url = u''
        urlTip = u''

    # 4gb Launcher
    class laa(object):
        name = u''          # Display name of the launcher
        exe = u'*DNE*'      # Executable to run
        launchesSE = False  # Whether the launcher will automatically launch the SE

    # Some stuff dealing with INI files
    class ini(object):
        # True means new lines are allowed to be added via INI tweaks
        #  (by default)
        allowNewLines = False
        # INI Entry to enable BSA Redirection
        bsaRedirection = (u'Archive', u'sArchiveList')

    # Save Game format stuff
    class ess(object):
        # Save file capabilities
        canReadBasic = True # Can read the info needed for the Save Tab display
        canEditMore = False # Advanced editing
        ext = u'.ess'       # Save file extension

    # INI setting used to setup Save Profiles
    #  (section,key)
    saveProfilesKey = (u'General', u'SLocalSavePath')

    # BAIN:
    #  These are the allowed default data directories that BAIN can install to
    dataDirs = {u'meshes', u'music', u'sound', u'textures', u'video'}
    #  These are additional special directories that BAIN can install to
    dataDirsPlus = set()
    # Files BAIN shouldn't skip
    dontSkip = ()
    # Directories where specific file extensions should not be skipped by BAIN
    dontSkipDirs = {}
    # Folders BAIN should never CRC check in the Data directory
    SkipBAINRefresh = set((
        # Use lowercase names
    ))
    # Files to exclude from clean data
    wryeBashDataFiles = {u'Docs\\Bash Readme Template.html',
                         u'Docs\\wtxt_sand_small.css', u'Docs\\wtxt_teal.css',
                         u'Docs\\Bash Readme Template.txt'}
    wryeBashDataDirs = {u'Bash Patches', u'INI Tweaks'}
    ignoreDataFiles = set()
    ignoreDataFilePrefixes = set()
    ignoreDataDirs = set()

    # Plugin format stuff
    class esp(object):
        # Wrye Bash capabilities
        canBash = False         # Can create Bashed Patches
        canCBash = False        # CBash can handle this game's records
        canEditHeader = False   # Can edit basic info in the TES4 record
        # Valid ESM/ESP header versions
        #  These are the valid 'version' numbers for the game file headers
        validHeaderVersions = tuple()
        # used to locate string translation files
        stringsFiles = [
            ((u'Strings',), u'%(body)s_%(language)s.STRINGS'),
            ((u'Strings',), u'%(body)s_%(language)s.DLSTRINGS'),
            ((u'Strings',), u'%(body)s_%(language)s.ILSTRINGS'),
        ]

    # Bash Tags supported by this game
    allTags = set()

    # Patcher available when building a Bashed Patch (referenced by class name)
    patchers = ()

    # CBash patchers available when building a Bashed Patch
    CBash_patchers = ()

    # Magic Info
    weaponTypes = ()

    # Race Info, used in faces.py
    raceNames = {}
    raceShortNames = {}
    raceHairMale = {}
    raceHairFemale = {}

    # Record information - set in cls.init ------------------------------------
    # Mergeable record types
    mergeClasses = ()
    # Extra read classes: these record types will always be loaded, even if patchers
    #  don't need them directly (for example, for MGEF info)
    readClasses = ()
    writeClasses = ()

    @classmethod
    def init(cls):
        # Setting RecordHeader class variables --------------------------------
        # Top types in order of the main ESM
        brec.RecordHeader.topTypes = []
        brec.RecordHeader.recordTypes = set(
            brec.RecordHeader.topTypes + ['GRUP', 'TES4'])
        # Record Types
        brec.MreRecord.type_class = dict((x.classType,x) for x in  (
                ))
        # Simple records
        brec.MreRecord.simpleTypes = (
                set(brec.MreRecord.type_class) - {'TES4'})

GAME_TYPE = None

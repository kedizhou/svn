# -*- encoding: utf8 -*-
__author__ = 'root'
import pysvn
import time


class svn:
    def __init__(self):
        self.client = pysvn.Client()
        self.interface = 'https://192.168.11.249/svn/www/test'
        self.client.callback_get_login = self.get_login
        self.client.callback_ssl_server_trust_prompt = self.ssl_server_trust_prompt
        self.client.callback_get_log_message = self.get_log_message
        self.log_min_entry = 0
        self.log_max_entry = 0

    def diff(self):
        diff_text = self.client.diff('/tmp/svn', '/data/svn/a', pysvn.Revision(pysvn.opt_revision_kind.number, 20825),
                                     '/data/svn/a', pysvn.Revision(pysvn.opt_revision_kind.number, 20826))
        return diff_text

    def get_log_message(self):
        # pysvn.ClientError
        log_message = "checkin,but not input message."
        return True, log_message

    def get_login(self, realm, user, may_save):
        return True, 'test', 'test', False

    def ssl_server_trust_prompt(self, trust_dict):
        return True, trust_dict['failures'], True

    '''
    last_changed_date : 1442383053.76
    kind : file
    last_changed_rev : <Revision kind=number 21067>
    last_changed_author : test
    URL : https://192.168.11.249/svn/www/test/xxxx.xx
    lock : None
    rev : <Revision kind=number 21165>
    repos_root_URL : https://192.168.11.249/svn/www
    wc_info : <PysvnWcInfo ''>
    repos_UUID : e8a990c7-5093-45c3-8e48-37132e9fcf2b
    '''

    def showversion(self, path=''):
        # path is 'locate file path'
        # info2 = self.client.info(path)
        # return info2['revision'].number
        info = self.client.info2(path)
        # for i in r[0][1]:
        #     print i, ':', r[0][1][i]
        return info[0][1]['last_changed_rev'].number

    def checkOut(self, path, version=0):
        # if directory depth grert than 1,auto make directory parent.
        # check out the current version of the pysvn project
        # self.client.checkout(self.interface, '/data/pysvn')
        # check out revision 11 of the pysvn project
        if version == 0:
            revision_max = pysvn.Revision(pysvn.opt_revision_kind.head)
        else:
            revision_max = pysvn.Revision(pysvn.opt_revision_kind.number, version)
        try:
            self.client.checkout(self.interface, path, revision=revision_max)
            # self.client.update( path, revision=revision_max, recurse=False)
            return True
        except Exception, e:
            print self.interface
            print 'ERROR: check out  path "' + path + '".', str(e).replace('pysvn._pysvn_2_7.ClientError:', '')
            return False

    def updateSpe(self, path, revision=0):
        if revision == 0:
            revision_max = pysvn.Revision(pysvn.opt_revision_kind.head)
        else:
            revision_max = pysvn.Revision(pysvn.opt_revision_kind.number, revision)
        try:
            self.client.update(path, revision=revision_max, recurse=True)
            return True
        except:
            print str(e).replace('pysvn._pysvn_2_7.ClientError:', '')
            return False

    def clean(self, path):
        self.client.cleanup(path)

    def rollBack(self, path='', version=0):
        print 'clean path: ' + path
        self.clean(path)
        print 'check out version: ' + str(version)
        self.checkOut(path=path, version=version)

    def checkNewest(self, path):
        self.client.update(path)

    def add(self, path, msg=''):
        # self.client.cleanup(path)
        # self.client.add(path, recurse=True, force=True, ignore=False, depth=None)
        self.client.add(path)
        self.client.checkin(path, msg)

    def remove(self, path):
        self.client.remove(path)
        self.client.checkin(path, 'delete ' + path)

    def submit(self, path):
        self.client.checkin(path, 'msg')

    '''
        return dir list [{'name': localname, 'type': str(type)} ...]
    '''

    def listSvnPath(self, path, recurse=True):
        # print 'path: ' + path
        flist = []
        flists = self.client.ls(path, revision=pysvn.Revision(pysvn.opt_revision_kind.head),
                                recurse=recurse,
                                peg_revision=pysvn.Revision(pysvn.opt_revision_kind.unspecified))
        for i in flists:
            localname = pysvn.PysvnDirent.items(i)[3][1]
            type = pysvn.PysvnDirent.items(i)[1][1]
            if localname:
                flist.append({'name': localname, 'type': str(type)})
        return flist

    def getlog(self, path='', tests=False):
        '''
        author - string - the name of the author who committed the revision
        date - float time - the date of the commit
        message - string - the text of the log message for the commit
        revision - pysvn.Revision - the revision of the commit
        changed_paths - list of dictionaries. Each dictionary contains:
            path - string - the path in the repository
            action - string
            copyfrom_path - string - if copied, the original path, else None
            copyfrom_revision - pysvn.Revision - if copied, the revision of the original, else None
        '''
        if not tests:
            entries = self.log_max_entry
        else:
            entries = self.log_min_entry
        return self.client.log(path, revision_start=pysvn.Revision(pysvn.opt_revision_kind.head),
                               revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, 0),
                               peg_revision=pysvn.Revision(pysvn.opt_revision_kind.unspecified),
                               discover_changed_paths=False,
                               limit=entries)

    def getsvnmsg(self, path, tests=False):
        # 检查项目
        sv = 0
        r = {}
        for i in self.getlog(path, tests):
            sv = sv + 1
            timeArray = time.localtime(i['date'])
            date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            # otherStyletime == "2013-10-10 23:40:00"
            # print 'msg:' + i['message'] + '.', 'date:', date, 'user:' + i['author'], 'version:', i['revision'].number
            tmp = []
            if len(i['changed_paths']) > 0:
                # print 'Changed paths:'
                for change_info in i['changed_paths']:
                    if change_info['copyfrom_path'] is None:
                        # print '  %s %s' % (change_info['action'], change_info['path'])
                        tmp.append({'action': change_info['action'], 'path': change_info['path']})
                    else:
                        tmp.append({'action': change_info['action'], 'path': change_info['path']})
                        # print  change_info['action'], change_info['path']
                        # change_info['copyfrom_path'], change_info[
                        # 'copyfro​m_revision'].number
            r[str(sv)] = {'msg': i['message'], 'date': date, 'user': i['author'], 'version': i['revision'].number,
                          'changed_paths': tmp}
        # print sv
        r['entry'] = sv
        return r

    def commit(self, path, msg):
        # , recurse=True, depth=1
        try:
            changes = self.client.status(path)
        except:
            # import sys
            # print sys.getdefaultencoding()
            import locale

            locale.setlocale(locale.LC_ALL, "")
            # print path
            # print isinstance(path.decode('gb2312'), unicode)
            changes = self.client.status(path)

        files = []
        for f in changes:
            f.path = f.path.encode('utf8')
            if str(f.text_status) == 'normal':
                continue

            print f.path, f.text_status
            if f.text_status == pysvn.wc_status_kind.obstructed:
                print 'obstructed:' + f.path, '您把.svn目录都给qj了.'

            if str(f.text_status) == 'missing':
                print 'file or directory:' + f.path + ' missing.'
                # self.checkOut(path)
                self.checkNewest(f.path)
                self.client.remove(f.path)
                # self.client.checkin(f.path, 'dele file or directory:' + f.path)
                files.append(f.path)

            if f.text_status == pysvn.wc_status_kind.added:
                print 'files to be added:', f.path
                try:
                    self.client.add(f.path)
                    # self.client.checkin(f.path, 'add file or path:' + f.path)
                    files.append(f.path)
                except Exception, e:
                    # self.client.remove(f.path)
                    # self.client.checkin(f.path, 'add file or path:' + f.path)
                    # self.client.add(f.path)
                    # self.client.checkin(f.path, 'add file or path:' + f.path)
                    # raise NameError, e
                    print e
                    pass

            if f.text_status == pysvn.wc_status_kind.deleted:
                print 'files or directory to be removed:', f.path
                self.checkNewest(f.path)
                self.client.remove(f.path)
                # self.client.checkin(f.path, 'dele file or directory:' + f.path)
                files.append(f.path)

            if f.text_status == pysvn.wc_status_kind.modified:
                print 'files that have changed:', f.path
                # self.client.checkin(f.path, 'modifle: ' + f.path)
                files.append(f.path)

            if f.text_status == pysvn.wc_status_kind.conflicted:
                print f.path

            if f.text_status == pysvn.wc_status_kind.unversioned:
                print 'unversioned files:', f.path
                try:
                    self.client.add(f.path)
                except:
                    raise NameError, u'遇到中文目录或者文件,提交失败.'

                # self.client.checkin(f.path, 'add file or path:' + f.path)
                files.append(f.path)
                # self.client.remove(f.path)
        if len(files) > 0:
            try:
                self.client.checkin(files, msg)
            except Exception, e:
                print path, 'is out of date; try updating.'
                if str(e).find('is out of date; try updating') + 1:

                    from os.path import isfile, isdir
                    from os import rename, remove

                    for i in files:
                        if isfile(i):
                            fpath = i.split('/')
                            fname = fpath.pop()
                            hidden = '/'.join(fpath) + '/.' + fname
                            if isfile(hidden):
                                remove(hidden)
                                print 'clean env.'
                            rename(i, '/'.join(fpath) + '/.' + fname)
                            try:
                                self.updateSpe(i)
                                remove(i)
                            except:
                                pass
                            rename(hidden, i)
                    self.client.checkin(files, msg)

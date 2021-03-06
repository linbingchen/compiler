# -*- coding: utf-8 -*-
from tool import Produce, Solution
import lexical_analyzer
import os
import sys


class PTree():

    def __init__(self, childlist=[], type=0, val=None, name=None):
        self.childlist = childlist
        self.type = type  # 1为叶子 0为中间节点
        self.val = val
        self.name = name
        self.tname=None


def iseql(prea, preb, posta, postb):
    return prea == preb and posta == postb


def flay(candidate):
    if type(candidate) != type([]):
        return candidate
    res = []
    for item in candidate:
        if type(item) == type([]):
            flayeditems = flay(item)
            for flayeditem in flayeditems:
                res.append(flayeditem)
        else:
            res.append(item)
    return res


def numtoken(res):
    if type(res) == type(1):
        return ('INT', res)
    else:
        return ('REAL', res)


class Var():

    def __init__(self, val, tp):
        self.val = val
        self.type = tp  # 0 integer 1 float

    def __unicode__(self):
        return str(self.val) + ',' + str(self.type)


class Parser():

    def __init__(self, intokens, parsetab, lexbuff):
        self.parsetab = parsetab
        self.lexbuff = lexbuff
        self.lexptr = 0
        self.stk = [0]
        self.stkitem = ["program'"]
        self.stknode = [PTree(name="program'")]
        self.ans = []
        self.intokens = intokens
        self.intokens.append('$')
        self.globevar = {}
        self.tid=0

    def tokentonum(self, tokenx):
        if(tokenx[0] == 'INT'):
            return int(tokenx[1])
        elif (tokenx[0] == 'REAL'):
            return float(tokenx[1])
        elif (tokenx[0] == 'ID'):
            return self.globevar[tokenx[1]].val
        else:
            print tokenx
            pass  # ! ID

    def semantic_analyze(self, pre, oripost, post):
        if oripost[0] != '\xa6\xc5' and len(oripost) == 1:
            # print '*,*'
            return post[0]
        else:
            ##
            return post
            ##
            if iseql(pre, 'simple_lexpression', oripost, ['simple_lexpression', 'laddop', 'lterm']):
                res = 0
                if post[1][0] == 'PLUS':
                    res = self.tokentonum(post[0]) + self.tokentonum(post[2])
                elif post[1][0] == 'MINUS':
                    res = self.tokentonum(post[0]) - self.tokentonum(post[2])
                elif post[1][0] == 'OR':
                    res = self.tokentonum(post[0]) | self.tokentonum(post[2])
                return numtoken(res)
                #!!! MUL
            elif iseql(pre, 'lprimary', oripost, ['lr_brac', 'lexpression', 'rr_brac']):
                return post[1]
            elif iseql(pre, 'lterm', oripost, ['lterm', 'lmulop', 'lfactor']):
                res = 0
                if post[1][0] == 'MULTI':
                    res = self.tokentonum(post[0]) * self.tokentonum(post[2])
                elif post[1][0] == 'RDIV' or post[1][0] == 'DIV':
                    res = self.tokentonum(post[0]) / self.tokentonum(post[2])
                elif post[1][0] == 'MOD':
                    res = self.tokentonum(post[0]) % self.tokentonum(post[2])
                elif post[1][0] == 'AND':
                    res = self.tokentonum(post[0]) & self.tokentonum(post[2])
                return numtoken(res)
            # lvariable_declaration -> llidentifier_list, colon, ltype_denoter
            elif iseql(pre, 'lvariable_declaration', oripost, ['llidentifier_list', 'colon', 'ltype_denoter']):
                ret = []
                if post[2][1].lower() == 'integer':
                    for item in post[0]:
                        if item == ('COMMA', 0):
                            continue
                        ret += item[1]
                        self.globevar[item[1]] = Var(0, 0)
                elif post[2][1].lower() == 'float':
                    for item in post[0]:
                        if item == ('COMMA', 0):
                            continue
                        ret += item[1]
                        self.globevar[item[1]] = Var(0.0, 1)
                return ret
            # lexponentiation -> lprimary, exp, lexponentiation
            elif iseql(pre, 'lexponentiation', oripost, ['lprimary', 'exp', 'lexponentiation']):
                res = self.tokentonum(post[0]) ** self.tokentonum(post[2])
                return numtoken(res)
            # aslsignment_lstatement -> lvariable_access, assign, lexpression
            elif iseql(pre, 'aslsignment_lstatement', oripost, ['lvariable_access', 'assign', 'lexpression']):
                self.globevar[post[0][1]].val = post[2][1]
                print "XD:" + self.globevar[post[0][1]].__unicode__()
                return post[2][1]
            else:
                return post

    def test(self):
        next = ('s', 15)
        tokbuf = [(('ID', 'e'), ('s', 15), 380), (('ASSIGN', 0), ('s', 271), 245), (('ID', 'e'), ('s', 15), 271), ((
            'MINUS', 0), ('s', 121), 281), (('INT', '1'), ('s', 63), 321), (('SEMIC', 0),)]
        tokptr = 0
        stk = [tokbuf[0][2]]
        stkitem = []
        brkfg = False
        while(1):
            if type(next) == type((1, 2)):
                if next[0] == 's':
                    stk.append(next[1])
                    stkitem.append(tokbuf[tokptr][0])
                    tokptr += 1
                elif next[0] == 'r':
                    tpost = []
                    if next[1].post[0] != '\xa6\xc5':
                        for j in range(len(next[1].post)):
                            if len(stkitem) <= 0:
                                brkfg = True
                                break
                            stk.pop()
                            tpost.append(stkitem.pop())
                        if brkfg:
                            break
                    tpost.reverse()
                    stk.append(self.parsetab[stk[len(stk) - 1]][next[1].pre])
                    stkitem.append(
                        self.semantic_analyze(next[1].pre, next[1].post, tpost))
                    print stkitem[len(stkitem) - 1]
                    print next[1].__unicode__()
            try:
                if type(next) != type((1, 2)) and 'closed_lstatement' == next[1].pre:
                    break;
                next = self.parsetab[
                    stk[len(stk) - 1]][tokbuf[tokptr][0][0].lower()]
            except:
                print tokbuf[tokptr]
                print tokbuf[tokptr][0]
                print tokbuf[tokptr][0][0].lower()
                print "error"
                break

    def play(self):
        sys.setrecursionlimit(8000)
        i = 0
        # print self.intokens
        # print self.intokens[i]
        # print self.stk[len(self.stk)-1]
        # print self.parsetab[self.stk[len(self.stk)-1]]
        next = self.parsetab[self.stk[len(self.stk) - 1]][self.intokens[i]]
        # print next
        ac = True
        while(next != "accept"):
            if type(next) == type((1, 2)):
                if next[0] == 's':
                    self.stk.append(next[1])
                    #self.stkitem.append((self.lexbuff[self.lexptr], next, self.stk[len(self.stk) - 2]))
                    self.stknode.append(PTree(
                        type=1, val=self.lexbuff[self.lexptr][1 if self.lexbuff[self.lexptr][0] in ['ID','REAL','INT'] else 0], name=self.lexbuff[self.lexptr][0]))
                    print 's'
                    print self.lexbuff[self.lexptr]
                    self.lexptr += 1
                    i += 1
                elif next[0] == 'r':
                    self.ans.append(next[1])
                    # print next[1].post
                    tpost = []
                    tnodes = []
                    if next[1].post[0] != '\xa6\xc5':
                        for j in range(len(next[1].post)):
                            # print (self.stk[len(self.stk)-1],next[1].post[j])
                            self.stk.pop()
                            #tpost.append(self.stkitem.pop())
                            tnodes.append(self.stknode.pop())
                    tpost.reverse()
                    tnodes.reverse()
                    self.stk.append(
                        self.parsetab[self.stk[len(self.stk) - 1]][next[1].pre])
                    #self.stkitem.append(self.semantic_analyze(next[1].pre, next[1].post, tpost))
                    self.stknode.append(PTree(childlist=tnodes, type=0 if(
                        next[1].post[0] != '\xa6\xc5') else 1, name=next[1].pre))
                    #print self.stkitem[len(self.stkitem) - 1]
                    if self.lexptr != len(self.lexbuff):
                        print self.lexbuff[self.lexptr]
                    print next[1].__unicode__()
            # print self.stk[len(self.stk)-1]
            # print self.parsetab[self.stk[len(self.stk)-1]]
            try:
                next = self.parsetab[
                    self.stk[len(self.stk) - 1]][self.intokens[i]]
                print next
            except:
                print "failed"
                ac = False
                break
            # print next
        # print self.ans
        print (self.stk)
        if ac:
            print "----------------------------------------"
            print "YaY!!Accept!!!!!"
            print "----------------------------------------"
            self.midrun(self.stknode[1])
        return self.ans



    def calexp(self,xnode): #lexpression node
        for child in xnode.childlist:
            self.calexp(child)

        if type==1:
            return
        else:
            if len(xnode.childlist)==1:
                if xnode.name=='lidentifier':
                    xnode.val=self.globevar[xnode.childlist[0].val].val
                    xnode.tname =xnode.childlist[0].val
                else:
                    xnode.val=xnode.childlist[0].val
                    xnode.tname=xnode.childlist[0].tname
            elif len(xnode.childlist)==2:
                if xnode.name=='lprimary':
                    xnode.val=not xnode.childlist[1].val
                    xnode.tname=xnode.childlist[1].tname
                    oriname=xnode.tname
                    if xnode.tname==None:
                        xnode.tname='t'+str(self.tid)
                        self.tid+=1
                        oriname=str(xnode.childlist[1].val)
                    print xnode.tname +'= not ' + oriname
                elif xnode.name=='lfactor':
                    xnode.val=( int(xnode.childlist[1].val) if xnode.childlist[0].val=='PLUS' else -int(xnode.childlist[1].val))
                    xnode.tname=xnode.childlist[1].tname
                    oriname=xnode.tname
                    if xnode.tname==None:
                        xnode.tname='t'+str(self.tid)
                        self.tid+=1
                        oriname=str(xnode.childlist[1].val)
                    print xnode.tname + ( '= + ' if xnode.childlist[0].val=='PLUS' else '= - ') + oriname
            elif len(xnode.childlist)==3:
                if xnode.name=='lprimary':
                    xnode.val=xnode.childlist[1].val
                else:
                    midop=(xnode.childlist[1].val)
                    preval=int(xnode.childlist[0].val)
                    postval=int(xnode.childlist[2].val)
                    prename=xnode.childlist[0].tname
                    postname=xnode.childlist[2].tname
                    xnode.tname='t'+str(self.tid)
                    self.tid+=1
                    resval=None
                    if prename==None:
                        prename=str(xnode.childlist[0].val)
                    if postname==None:
                        postname=str(xnode.childlist[2].val)
                    print   xnode.tname + ' = '+prename+' '+midop+' '+postname
                    if midop=='EXP':
                        resval= preval ** postval
                    elif midop=='MULTI':
                        resval = preval * postval
                    elif midop=='RDIV' or midop=='DIV':
                        resval = preval / postval
                    elif midop=='MOD':
                        resval = preval % postval
                    elif midop=='AND':
                        resval = preval and postval
                    elif midop=='PLUS':
                        resval = preval + postval
                    elif midop=='MINUS':
                        resval = preval - postval
                    elif midop=='OR':
                        resval = preval or postval
                    elif midop=='EQ':
                        resval = preval == postval
                    elif midop=='NE':
                        resval = preval != postval
                    elif midop=='LT':
                        resval = preval < postval
                    elif midop=='GT':
                        resval = preval > postval
                    elif midop=='LE':
                        resval = preval <= postval
                    elif midop=='GE':
                        resval = preval >= postval
                    xnode.val=resval
        return xnode.val

    def getvar(self,xnode):
        for child in xnode.childlist:
            self.declarevar(child)

        if type==1:
            return xnode.val
        else:
            if len(xnode.childlist)==1:
                xnode.val=xnode.childlist[0].val
                return xnode.val
            return None

    def setvar(self,valname,value):
        self.globevar[valname].val=value
        return

    def declarevar(self,xnode): #llvariable_declaration_list
        for child in xnode.childlist:
            self.declarevar(child)

        if type==1:
            return
        else:
            if len(xnode.childlist)==1:
                if xnode.name=='llidentifier_list':
                    xnode.val=[xnode.childlist[0].val]
                else:
                    xnode.val = xnode.childlist[0].val
            elif len(xnode.childlist)==3:
                if xnode.name=='llidentifier_list':
                    print type(xnode.val)
                    xnode.val=xnode.childlist[0].val
                    xnode.val.append(xnode.childlist[2].val)
                elif xnode.name=='lvariable_declaration':
                    typename = xnode.childlist[2].val.lower()
                    tc=0
                    if typename=='integer':
                        tc=0
                    elif typename=='float':
                        tc=1
                    for varname in xnode.childlist[0].val:
                        self.globevar[varname]=Var(0,tc)

    def midrun(self,xnode):
        #print xnode.name
        #print xnode.val

        retfg=False
        if xnode.name=='llvariable_declaration_part':
            retfg=True
            self.declarevar(xnode.childlist[1])
            print 'ok'
        elif xnode.name=='closed_while_lstatement' or xnode.name=='open_while_lstatement':
            retfg=True
            cdtfg=self.calexp(xnode.childlist[1])
            while cdtfg:
                self.midrun(xnode.childlist[3])
                cdtfg=self.calexp(xnode.childlist[1])
        elif xnode.name=='open_if_lstatement' or xnode.name=='closed_if_lstatement':
            retfg=True
            if len(xnode.childlist)==4:
                cdtfg=self.calexp(xnode.childlist[1])
                if cdtfg:
                    self.midrun(xnode.childlist[3])
            elif len(xnode.childlist)==6:
                cdtfg=self.calexp(xnode.childlist[1])
                if cdtfg:
                    self.midrun(xnode.childlist[3])
                else:
                    self.midrun(xnode.childlist[5])
        elif xnode.name=='aslsignment_lstatement':
            retfg=True
            varname =self.getvar(xnode.childlist[0])
            self.globevar[varname].val=self.calexp(xnode.childlist[2])
            oriname=xnode.childlist[2].tname
            if oriname==None:
                oriname=str(xnode.childlist[2].val)
            print varname + ' = ' + oriname
            #self.setvar(self.getvar(xnode.childlist[0]),self.calexp(xnode.childlist[2]))
            print 'assign ok! varname:'+varname \
                  +' ,varval:'+ str(self.globevar[varname].val)
        if retfg:
            return

        for child in xnode.childlist:
            self.midrun(child)

        # if xnode.type


cnm = lexical_analyzer.Solution()
prefix = ''
if os.name == 'nt':
    prefix = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '\\'
file_object = open(prefix + 'code.txt')
text = ""
try:
    text = file_object.read()
except:
    print 'error'
hehe = cnm.lex_analyzer(text)
#######################

ans = {}
with open(os.name == 'nt' and prefix + "lower_tab" or "lower_tab", 'r') as f:
    raw_str = f.read()
    sol = Solution()
    ans = sol.table_analyzer(raw_str)
#################################
# print [item[0].lower() for item in hehe]
# print ans
# print "toolok"
ok = Parser([item[0].lower() for item in hehe], ans,hehe)
ret = ok.play()
# ok.test()
# for i in range(len(ret) - 1, -1, -1):
#    print ret[i].__unicode__()

# print hehe


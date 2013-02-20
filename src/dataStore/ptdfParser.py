#!/usr/bin/env python2.7
import ply.lex as lex
import ply.yacc as yacc
from PTds import *

class PTDFLexer:   
    def __init__(self):
        self.reserved = {
            'Application' : 'APPLICATION',
            'ResTypeHierArchy' : 'RESTYPEHIERARCHY',
            'ResourceType' : 'RESOURCETYPE',
            'Execution' : 'EXECUTION',
            'Resource' : 'RESOURCE',
            'ResourceAttribute' : 'RESOURCEATTRIBUTE',
            'ResourceConstraint' : 'RESOURCECONSTRAINT',
            'Context' : 'CONTEXT',
            'PerfResult' : 'PERFRESULT',
            'Result': 'RESULT',
            'ComplexResult': 'COMPLEXRESULT'
            }
        self.tokens = ['QUOTED', 'NAME'] + list(self.reserved.values())
        self.lexer = lex.lex(module=self,)

    # Tokens
    def t_QUOTED(self, t):
        r'"([^"]+)"'
        t.value = t.value[1:-1]
        return t;

    # Ignored characters
    t_ignore = " "
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def t_NAME(self, t):
        r'\S+'
        t.type = self.reserved.get(t.value,'NAME')    # Check for reserved words
        return t

    precedence = ()

class PTDFParser:
    def __init__(self, ptds):
        self.ptds = ptds
        self.lexer = PTDFLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self,write_tables=0,debug=False,start='ptdf')

    def parse(self,data):
        if data:
            self.parser.parse(data,self.lexer.lexer,0,0,None)
        else:
            return []

    def p_error(self, p):
        print("Syntax error at token", p.type , "line ", p.lineno)

    def p_string(self, p):
        '''string : QUOTED 
                  | NAME '''
        p[0] = p[1]

    def p_ptdf(self, p) :
        '''ptdf : statement ptdf
                | lambda'''
        pass

    def p_statement(self, p):
        '''statement : application 
                     | restypehierarchy
                     | resourcetype
                     | execution
                     | resource
                     | resourceconstraint
                     | resourceattribute
                     | context
                     | perfresult
                     | result
                     | complexresult'''
        pass

    def p_lambda(self, p):
        'lambda : '
        pass

    def p_res_type_name(self, p):
        'res_type_name : string'
        p[0] = p[1].replace(self.ptds.dataDelim, self.ptds.dbDelim)

    def p_application(self, p):
        'application : APPLICATION string'
        self.ptds.addApplication(p[2])
        
    def p_restypehierarchy(self, p):
        'restypehierarchy : RESTYPEHIERARCHY res_type_name'
        self.ptds.addResTypeHierarchy(p[2])        

    def p_resourcetype(self, p):
        'resourcetype : RESOURCETYPE res_type_name'
        self.ptds.addResType(p[2])

    def p_execution(self, p):
        'execution : EXECUTION string string'
        self.ptds.addExecution(p[2], p[3])

    def p_resource(self, p):
        '''resource : RESOURCE string res_type_name
                    | RESOURCE string res_type_name string'''
        if (len(p) == 5):
            self.ptds.addExecResource(p[2], p[3], p[4])
        else:
            self.ptds.addResource(p[2], p[3])

    def p_resourceconstraint(self, p):
        'resourceconstraint : RESOURCECONSTRAINT string string'
        self.ptds.addResourceConstraint(p[2], p[3])

    def p_resourceattribute(self, p):
        'resourceattribute : RESOURCEATTRIBUTE string string string string'
        self.ptds.addResourceAttribute(p[2], p[3], p[4], p[5])

    def p_context(self, p):
        'context : CONTEXT string string'
        self.ptds.addContextAlias(p[2], p[3]) 

    def p_perfresult(self, p):
        'perfresult : PERFRESULT string string string string string string string string'
        self.ptds.addPerfResult(p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

    def p_result(self, p):
        'result : RESULT string string string string string string string string'
        self.ptds.addResult(p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

    def p_complexresult(self, p):
        'complexresult : COMPLEXRESULT string string string string string string string'
        self.ptds.addComplexResult(p[2], p[3], p[4], p[5], p[6], p[7], p[8])

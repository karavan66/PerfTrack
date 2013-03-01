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
        self.tokens = ['QUOTED', 'NAME', 'NEWLINE'] + list(self.reserved.values())
        self.lexer = lex.lex(module=self,debug=False)

    # Tokens
    def t_QUOTED(self, t):
        r'"([^"]+)"'
        t.value = t.value[1:-1]
        return t;

    # Ignored characters
    t_ignore = " "
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return t

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

    def __error(self, p, syntax):
        self.ptds.log.error("Syntax Error %s:%s -> %s", self.ptds.filename, p.lineno(1), syntax)
        raise Exception("PTDF Syntax Error %s:%s" % (self.ptds.filename, p.lineno(1)))

    def parse(self,data):
        if data:
            # useful for just dumping lexer tokens
            #self.lexer.lexer.input(data)
            #for t in self.lexer.lexer:
            #    print t
            self.parser.parse(data,self.lexer.lexer,0,0,None)
        else:
            return []

    def p_error(self, p):
        print("Syntax error at token %s filename %s line %s" % (p.type , self.ptds.filename, p.lineno))

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
                     | complexresult
                     | NEWLINE'''

    def p_lambda(self, p):
        'lambda : '
        pass

    def p_res_type_name(self, p):
        'res_type_name : string'
        p[0] = p[1].replace(self.ptds.dataDelim, self.ptds.dbDelim)

    def p_application(self, p):
        'application : APPLICATION string NEWLINE'
        self.ptds.addApplication(p[2])
    
    def p_application_error(self, p):
        'application : APPLICATION error NEWLINE'
        self.__error(p, "Application <AppName>")

    def p_restypehierarchy(self, p):
        'restypehierarchy : RESTYPEHIERARCHY res_type_name NEWLINE'
        self.ptds.addResTypeHierarchy(p[2])        

    def p_restypehierarchy_error(self, p):
        'restypehierarchy : RESTYPEHIERARCHY error NEWLINE'
        self.__error(p, "ResTypeHierarchy <resHierarchyName>")

    def p_resourcetype(self, p):
        'resourcetype : RESOURCETYPE res_type_name NEWLINE'
        self.ptds.addResType(p[2])

    def p_resourcetype_error(self, p):
        'resourcetype : RESOURCETYPE error NEWLINE'
        self.__error(p, "ResourceType <resTypeName>")

    def p_execution(self, p):
        'execution : EXECUTION string string NEWLINE'
        self.ptds.addExecution(p[2], p[3])

    def p_execution_error(self, p):
        'execution : EXECUTION error NEWLINE'
        self.__error(p, "Execution <execName> <appName>")

    def p_resource(self, p):
        '''resource : RESOURCE string res_type_name NEWLINE
                    | RESOURCE string res_type_name string NEWLINE'''
        if (len(p) == 6):
            self.ptds.addExecResource(p[2], p[3], p[4])
        else:
            self.ptds.addResource(p[2], p[3])

    def p_resource_error(self, p):
        '''resource : RESOURCE error NEWLINE'''
        self.__error(p, "Resource <resourceName> <resourceTypeName> [<execName>]")

    def p_resourceconstraint(self, p):
        'resourceconstraint : RESOURCECONSTRAINT string string NEWLINE'
        self.ptds.addResourceConstraint(p[2], p[3])

    def p_resourceconstraint_error(self, p):
        'resourceconstraint : RESOURCECONSTRAINT error NEWLINE'
        self.__error(p, "ResourceConstraint <resourceName1> <resourceName2>")

    def p_resourceattribute(self, p):
        '''resourceattribute : RESOURCEATTRIBUTE string string string string NEWLINE'''
        self.ptds.addResourceAttribute(p[2], p[3], p[4], p[5])

    def p_resourceattribute_error(self, p):
        '''resourceattribute : RESOURCEATTRIBUTE error NEWLINE'''
        self.__error(p, "ResourceAttribute <resName><attribute><value><attributeType>")

    def p_context(self, p):
        'context : CONTEXT string string NEWLINE'
        self.ptds.addContextAlias(p[2], p[3]) 

    def p_context_error(self, p):
        'context : CONTEXT error NEWLINE'
        self.__error(p, "Context <contextName> <resourceList>")

    def p_perfresult(self, p):
        'perfresult : PERFRESULT string string string string string string string string NEWLINE'
        self.ptds.addPerfResult(p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

    def p_perfresult_error(self, p):
        'perfresult : PERFRESULT error NEWLINE'
        self.__error(p, "PerfResult <execName> "
                     "<focusName> <perfToolName> <metricName> <value> "
                     "<units> <startTime> <endTime>""Context <contextName> <resourceList>")

    def p_result(self, p):
        'result : RESULT string string string string string string string string NEWLINE'
        self.ptds.addResult(p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])

    def p_result_error(self, p):
        'result : RESULT error NEWLINE'
        self.__error(p, "Result <resourceName> "
                     "<focusName> <perfToolName> <metricName> <value> "
                     "<units> <startTime> <endTime>")

    def p_complexresult(self, p):
        'complexresult : COMPLEXRESULT string string string string string string string NEWLINE'
        self.ptds.addComplexResult(p[2], p[3], p[4], p[5], p[6], p[7], p[8])

    def p_complexresult_error(self, p):
        'complexresult : COMPLEXRESULT error NEWLINE'
        self.error(p, "ComplexResult <focusName> "
                   "<perfToolName> <metricName> <values> "
                   "<units> <startTimes> <endTimes>")

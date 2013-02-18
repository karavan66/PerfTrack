# PerfTrackDataFormat, by Steve Wooster, 2/14/2006 2:05PM
## filename: ptdf.py
from datetime import datetime

# PTDF attribute tree:
# ptdf
#     .add
#         .resources["name"]
#                           .name (redundant)
#                           .type
#                           .date
#                           .resources["name"]
#                                             ...
#                           .attributes["name"]
#                                              .name (redundant)
#                                              .value
#                                              .date
#                                              .type (redundant?)
#                           .constraints[index] == ("list","of","resource","names") ?
#     .sub (same as .add)

class PerfTrackDataFormat:
    """PerfTracDataFormat object.

    Used to construct and output PTDF files.
    """

    resDelim = "|" # the delimiter for separating hierarchical resources

    class ModificationTree:
        """A tree of modifications to list in a PTDF file."""

        def __init__( self ):
            self.resources = {}
            # a dictionary to hold all the resource types we've encountered
            # the types are the keys, there is no value. we are just using 
            # a dictionary as a shortcut to eliminate duplicates in the 
            # list of types
            self.types = {}
            self.resDelim = PerfTrackDataFormat.resDelim

        def __setitem__( self, key, value ):
            key = PerfTrackDataFormat.Argument2List( key )
            value = PerfTrackDataFormat.Argument2List( value )

            # add length checks?

            # Find out wether or not a time was specified.
            time = None
            try:
                if value[-1].__class__ is datetime:
                    time = value[-1]
                    value = value[0:-1]
            except AttributeError:
                pass

            class NoReplace:
                pass

            # If necessary, expand a single type into a list of types.
            if len(value) == 1:
                # Format: [ NoReplace, ... , NoReplace, value[0] ]
                value = [ NoReplace for i in range( len(key)-1 ) ] + value
            elif len(value) != len(key):
                errMsg = "Wrong number of PTDF types set. Expected: " + str(len(key)) + " Got: " + str(len(value))
                raise TypeError, errMsg

            # Check to make sure that key is a valid resource list.
            r = PerfTrackDataFormat.Resource()
            for name, type in zip( key, value ):
                r.validateName( name )
                if type is not NoReplace:
                    r.validateType(type)

            # take the list of types and make a string out of it
            fullType = ""
            for v in value:
               fullType += "%s%s" % (self.resDelim,v)
            fullType = fullType.lstrip(self.resDelim)  # strip off leading /
            # add it to the dictionary of types
            self.types[fullType] = ''
            

            # Go down the list, setting up the tree.
            currentTreeNode = self
            for name, type in zip( key, value ):
                if not name in currentTreeNode.resources:
                    # Create a new resource
                    currentTreeNode.resources[name] = PerfTrackDataFormat.Resource( name )
                currentTreeNode = currentTreeNode.resources[name]
                if type is not NoReplace:
                    currentTreeNode.type = type
                    currentTreeNode.time = time

        def __getitem__( self, key ):
            key = PerfTrackDataFormat.Argument2List( key )
            # check key?

            currentTreeNode = self
            for name in key:
                if not name in currentTreeNode.resources:
                    raise KeyError(key)
                currentTreeNode = currentTreeNode.resources[name]
            return currentTreeNode

        def __delitem__( self, key ):
            key = PerfTrackDataFormat.Argument2List( key )
            # check key?

            parent = None
            currentTreeNode = self
            for name in key:
                if not name in currentTreeNode.resources:
                    raise KeyError(key)
                parent = currentTreeNode
                currentTreeNode = currentTreeNode.resources[name]
            if parent:
                del parent.resources[name]

        def iterDefineResourceTypes(self):
            # grab all the types we've seen in to a list
            types = self.types.keys()
            # sort it
            types.sort() 
            # output ResourceType lines
            for type in types:
                yield "ResourceType %s\n" % type

        def iterDefineResources( self, defineConstraints = False ):
            for resource in self.resources.itervalues():
                #for line in resource.iterDefineResources(self.resDelim,"", defineConstraints ):
                for line in resource.iterDefineResources("","", defineConstraints ):
                    yield line

    class Resource:
        """A perftrack resource."""

        def __init__( self, name = None, type = None, time = None ):
            self.resDelim = PerfTrackDataFormat.resDelim
            self.validateName(name);
            self.validateType(type);
            self.name = name
            self.type = type
            self.time = time
            self.resources = {}
            self.attributes = {}
            self.constraints = {}

        def __setitem__( self, key, value ):
            attribute = None
            try:
                if value.__class__ is PerfTrackDataFormat.Attribute:
                    attribute = PerfTrackDataFormat.Attribute(value)
                    attribute.name = key
                elif value.__class__ is tuple:
                    if len(value) != 2:
                        errMsg = "Expecting 2 arguments, but got " + str(len(value)) + "."
                        raise TypeError, errMsg
                    attribute = PerfTrackDataFormat.Attribute( key, value[0], value[1] )
            except AttributeError:
                pass
            if not attribute:
                attribute = PerfTrackDataFormat.Attribute( key, value )
            self.attributes[key] = attribute

        def __getitem__( self, key ):
            return self.attributes[key]

        def __delitem__( self, key ):
            del self.attributes[key]

        def addConstraint( self, *value ):
            if len(value) == 1:
                value = value[0]
            value = PerfTrackDataFormat.Argument2List( value )

            time = None
            try:
                if value[-1].__class__ is datetime:
                    time = value[-1]
                    value = value[0:-1]
            except AttributeError:
                pass

            self.constraints[tuple(value)] = PerfTrackDataFormat.Constraint( value, time )

        def delConstraint( self, *value ):
            if len(value) == 1:
                value = value[0]
            value = PerfTrackDataFormat.Argument2List( value )
            del self.constraints[tuple(value)]

        def validateName(self, name ):
            if name is None:
                return
            if len(name) > 64:
                raise ValueError( "Resource name length is longer than 64" )
            for str in [ self.resDelim, "::", ",", "####", "(", ")" ]:
                if str in name:
                    raise ValueError( "Resource name contains substring: "+str )
        #validateName = staticmethod( validateName );

        def validateType( self,type ):
            if type is None:
                return
            if len(type) > 128:
                raise ValueError( "Resource type length is longer than 128" )
            for str in [ self.resDelim ]:
                if str in type:
                    raise ValueError( "Resource type contains substring: "+str )
        #validateType = staticmethod( validateType );

        def iterDefineResources( self, parentPath, parentPathType, defineConstraints = False ):
            if self.type is None:
                raise RuntimeError( "Resource " + parentPath + self.name + " has no type" )

            parentPath     += self.name
            parentPathType += self.type

            ## Take care of front of resource name with white space
            if parentPath[1] == '"':
               #tmpStr = '"%s' % self.resDelim
               tmpStr = ""
               for x in range(2,len(parentPath)):
                  tmpStr = tmpStr + parentPath[x]
               parentPath = tmpStr

            if defineConstraints:
                # Define our constraints
                for constraint in self.constraints.itervalues():
                    for line in constraint.iterDefineConstraint( parentPath ):
                        yield line

            else:
                addEndQuote = False
                ## Take care of end of resource name with white space
                if parentPath[0] == '"' and \
                   parentPath[len(parentPath)-1] != '"':
                    parentPath = parentPath + '"'
                    addEndQuote = True
                # Define ourself
                yield "Resource " + parentPath + " " + parentPathType + "\n"

                # Define our attributes
                for attribute in self.attributes.itervalues():
                    for line in attribute.iterDefineAttribute( parentPath ):
                        yield line
                if addEndQuote:
                    parentPath = parentPath.rstrip('"') 

            parentPath     += self.resDelim
            parentPathType += self.resDelim
            #print "iterDefineResources: parentPath: %s" % (parentPath)
            #print "iterDefineResources: parentPathType: %s" % (parentPathType)
            # Define child resources
            for resource in self.resources.itervalues():
                for line in resource.iterDefineResources( parentPath, parentPathType, defineConstraints ):
                    yield line

    class Attribute:
        """A perftrack resource attribute."""

        def __init__( self, name = None, value = None, time = None, type = "string" ):
            try: # If we were passed another Attribute, copy it.
                if name.__class__ is self.__class__:
                    value = name.value
                    time = name.time
                    type = name.type
                    name = name.name
            except AttributeError:
                pass

            self.name = name
            self.value = value
            self.time = time
            self.type = type
            self.resDelim = PerfTrackDataFormat.resDelim

        def validateName( name ):
            if len(name) > 64:
                raise ValueError( "Attribute name length is longer than 64" )
            for str in [ " ", self.resDelim ]:
                if str in name:
                    raise ValueError( "Attribute name contains substring: "+str )
            return True
        validateName = staticmethod( validateName );

        def iterDefineAttribute( self, parentResource ):
            yield "ResourceAttribute " + parentResource + " " + self.name + " " + self.value + " " + self.type + "\n"

    class Constraint:
        """A perftrack resource constraint."""

        def __init__( self, resource = [], time = None ):
            for name in resource:
                PerfTrackDataFormat.Resource.validateName( name )
            self.resource = resource
            self.time = time
            self.resDelim = PerfTrackDataFormat.resDelim

        def iterDefineConstraint( self, parentResource ):
            resource = ""
            for name in self.resource:
                resource += self.resDelim + name
                resource = resource.lstrip(self.resDelim)
            yield "ResourceConstraint " + parentResource + " " + resource + "\n"

    # NYI
    class Unknown:
        """ Unknown name type. """
        pass

    def __init__( self ):
        self.defaultTime = datetime.now()
        self.add = self.ModificationTree()
        self.sub = self.ModificationTree()

    def __pos__( self ):
        return self.add
    def __neg__( self ):
        return self.sub

    def __setitem__( self, resource, type ):
        (+self)[resource] = type
    def __getitem__( self, resource ):
        return (+self)[resource]
    def __delitem__( self, resource ):
        del (+self)[resource]

    def __iter__( self ):
        # <define removals?>

        # define resource types
        for line in self.add.iterDefineResourceTypes():
            yield line

        # Define resources
        for line in self.add.iterDefineResources():
            yield line

        # Define constraints
        for line in self.add.iterDefineResources( True ):
            yield line

    def Argument2List( arg ):
        """Copies its argument to a list.
        If the argument is a list, it returns a copy.
        If the argument is a tuple, it returns a list with the same contents.
        Else, it returns a list whose only element is the argument.
        """
        try:
            if arg.__class__ in (list, tuple):
                return list( arg )
        except AttributeError:
            pass
        return [ arg ]
    Argument2List = staticmethod( Argument2List )



from .IntHolderConverter import IntHolderConverter

def register_converters():
    from autowrap.ConversionProvider import  special_converters
    special_converters.append(IntHolderConverter())

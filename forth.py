import copy, tools
#contract={}
#put get runfunc stop n-dup n-swap n-roll hash int unico
op_fee=100
func_fee=100
def cost(state):
    n=state['stack'].pop()
    state['gas']-=int(n)
    return state
def integer(state):
    n=state['stack'].pop()
    state['stack'].append(int(n))
    return state
def dupn(state):
    n=state['stack'].pop()
    state['stack']+=state['stack'][-n:]
    return state
def swapn(state):
    n=state['stack'].pop()
    state['stack']=state['stack'][:2*n]+state['stack'][n:]+state['stack'][2*n:n]
    return state
def put_func(state):
    value=state['stack'].pop()
    key=state['stack'].pop()
    state['mem'][key]=value
    return state
def get(state):
    key=state['stack'].pop()
    val=state['mem'][key]
    state['stack'].append(val)
    return state
def drop(state):
    state['stack'].pop()
    return state
def binary(state, func):
    a=state['stack'].pop()
    b=state['stack'].pop()
    state['stack'].append(func(a, b))
    return state
def mul(a, b): return a*b
def div(a, b): return a/b
def minus(a, b): return a-b
def plus(a, b): return a+b
ex_language={'swapn':swapn,
             'dupn':dupn,
             'get':get,
             'drop':drop,
             '*':lambda s: binary(s, mul),
             '/':lambda s: binary(s, div),
             '+':lambda s: binary(s, plus),
             '-':lambda s: binary(s, minus)}
def read_string(code, s=''):
    if code[0]=="'": return s, code[1:]
    infix=''
    if s!='': infix=' '
    return read_string(code[1:], s+infix+code[0])
def read_definitions(code):
    if type(code) in [str, unicode]:
        code=code.split(' ')
    mem={}
    b=False
    val=''
    while code!=[]:
        n=code[0]
        if n=='fn':
            if b: return 'errr on :'
            b=True
            key=code[1]
            code=code[2:]
            val=''
        if n=='end':
            if not b: return 'error on ;'
            b=False
            mem[key]=val
        if val!='':
            val+=' '
        val+=code[0]
        code=code[1:]
    return mem
def forth(code, language, state):
    return forth_helper(code, language, copy.deepcopy(state))
def forth_helper(code, language, state):
    if type(state)==list:
        return state
    if 0>state['gas']:
        return ['not enough gas']
    if type(code)!=list:
        code=code.split(' ')
    if len(code)==0: return state
    try: 
        code[0]=int(code[0])
        state['stack'].append(code[0])
        return forth_helper(code[1:], language, state)
    except Exception as exc:
        #tools.log(exc)
        pass
    if code[0]==".'":
        string, code =read_string(code[1:])
        state['stack'].append(string)
        return forth_helper(code, language, state)
    if code[0] in language:
        state['gas']-=op_fee
        return forth_helper(code[1:], language, language[code[0]](state))
    if code[0] in state['mem']:
        state['gas']-=func_fee
        language['put']=put_func
        return forth_helper(code[1:], language, forth(state['mem'][code[0]], language, state))
    else:
        return ['error undefined word: ' +str(code[0])]
def test_get():
    default_state={'mem':{'contract_func':"it works"},'stack':[], 'gas':100000}
    ex_script=".' contract_func ' get"
    print(forth(ex_script, ex_language, default_state))
def test_put():
    default_state={'mem':{'contract_func':"put"},'stack':[], 'gas':100000}
    ex_script=".' a b ' .' by zack ' contract_func"
    print(forth(ex_script, copy.deepcopy(ex_language), default_state))
    ex_script=".' a b ' .' by zack ' put"
    print(forth(ex_script, copy.deepcopy(ex_language), default_state))#this one should fail
#test_get()
#test_put()

    #memory for code and data should work the same way.
    #only built-in scripts should be able to use 'put' to modify memory directly. Users can call the built-in scripts, but they cannot call 'put' directly.

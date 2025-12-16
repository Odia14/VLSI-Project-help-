import heapq
from itertools import product

class Wire:
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.last_change_time = -1
        self.listeners = []

class NAND:
    def __init__(self, in1, in2, out, delay=1):
        self.in1 = in1
        self.in2 = in2
        self.out = out
        self.delay = delay
        in1.listeners.append(self)
        in2.listeners.append(self)

    def compute(self):
        return 0 if self.in1.value and self.in2.value else 1

class Simulator:
    def __init__(self):
        self.time = 0
        self.events = []
        self.event_id = 0

    def schedule(self, gate, dt):
        heapq.heappush(self.events, (self.time + dt, self.event_id, gate))
        self.event_id += 1

    def run_until_stable(self):
        while self.events:
            t, eid, gate = heapq.heappop(self.events)
            if t > self.time:
                self.time = t
            new_val = gate.compute()
            if new_val != gate.out.value:
                gate.out.value = new_val
                gate.out.last_change_time = self.time
                for listener in gate.out.listeners:
                    self.schedule(listener, listener.delay)

def set_inputs(values, input_wires, sim):
    for i, val in enumerate(values):
        if input_wires[i].value != val:
            input_wires[i].value = val
            input_wires[i].last_change_time = sim.time
            for listener in input_wires[i].listeners:
                sim.schedule(listener, listener.delay)

def create_fa(A, B, CIN, SUM, COUT, delay=1):
    temp1 = Wire('temp1')
    temp2 = Wire('temp2')
    temp3 = Wire('temp3')
    P = Wire('P')
    temp4 = Wire('temp4')
    temp5 = Wire('temp5')
    temp6 = Wire('temp6')
    temp10 = Wire('temp10')
    NAND(A, B, temp1, delay)
    NAND(A, temp1, temp2, delay)
    NAND(B, temp1, temp3, delay)
    NAND(temp2, temp3, P, delay)
    NAND(P, CIN, temp4, delay)
    NAND(P, temp4, temp5, delay)
    NAND(CIN, temp4, temp6, delay)
    NAND(temp5, temp6, SUM, delay)
    NAND(P, CIN, temp10, delay)
    NAND(temp1, temp10, COUT, delay)

def create_rca(delay=1):
    A = [Wire(f'A{i}') for i in range(4)]  # A0 to A3
    B = [Wire(f'B{i}') for i in range(4)]  # B0 to B3
    CIN = Wire('CIN')
    S = [Wire(f'S{i}') for i in range(4)]
    COUT = Wire('COUT')
    C1 = Wire('C1')
    C2 = Wire('C2')
    C3 = Wire('C3')
    create_fa(A[0], B[0], CIN, S[0], C1, delay)
    create_fa(A[1], B[1], C1, S[1], C2, delay)
    create_fa(A[2], B[2], C2, S[2], C3, delay)
    create_fa(A[3], B[3], C3, S[3], COUT, delay)
    input_wires = A + B + [CIN]
    return input_wires, S[3], COUT

# Main simulation
input_wires, S3, COUT = create_rca()

max_rise_s3 = 0
vec_rise_s3 = None
max_fall_s3 = 0
vec_fall_s3 = None
max_rise_cout = 0
vec_rise_cout = None
max_fall_cout = 0
vec_fall_cout = None

all_states = list(product([0, 1], repeat=9))  # All 512 input combinations

for old in all_states:
    for new in all_states:
        if old == new:
            continue
        sim = Simulator()
        set_inputs(old, input_wires, sim)
        sim.run_until_stable()
        old_s3 = S3.value
        old_cout = COUT.value
        S3.last_change_time = -1
        COUT.last_change_time = -1
        sim.events = []
        sim.time = 0
        set_inputs(new, input_wires, sim)
        sim.run_until_stable()
        if S3.last_change_time > -1 and S3.value != old_s3:
            delay = S3.last_change_time
            if S3.value == 1 and delay > max_rise_s3:
                max_rise_s3 = delay
                vec_rise_s3 = (old, new)
            elif S3.value == 0 and delay > max_fall_s3:
                max_fall_s3 = delay
                vec_fall_s3 = (old, new)
        if COUT.last_change_time > -1 and COUT.value != old_cout:
            delay = COUT.last_change_time
            if COUT.value == 1 and delay > max_rise_cout:
                max_rise_cout = delay
                vec_rise_cout = (old, new)
            elif COUT.value == 0 and delay > max_fall_cout:
                max_fall_cout = delay
                vec_fall_cout = (old, new)

print('Max rise S3:', max_rise_s3, 'vector:', vec_rise_s3)
print('Max fall S3:', max_fall_s3, 'vector:', vec_fall_s3)
print('Max rise Cout:', max_rise_cout, 'vector:', vec_rise_cout)
print('Max fall Cout:', max_fall_cout, 'vector:', vec_fall_cout)
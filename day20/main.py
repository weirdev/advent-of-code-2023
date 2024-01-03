from typing import List, Tuple, Dict, Optional
from collections import deque
import itertools

global_state = 0

class Module:
    """Low pulse == False, High pulse == True"""
    low_pulse_count = 0
    high_pulse_count = 0

    def __init__(self, name: str):
        self.outputs: ['Module'] = []
        self.name = name

    def add_input(self, input: 'Module') -> None:
        # Can be overridden by subclasses
        pass

    def _get_pulse_output(self, pulse_input: bool, input_module: 'Module') -> Optional[bool]:
        # Must be overridden by subclasses
        raise NotImplementedError()

    def __call__(self, pulse_input: bool, input_module: 'Module') -> [Tuple['Module', bool, 'Module']]:
        """Returns [(output, pulse, input_module=self)]"""
        if pulse_input:
            Module.high_pulse_count += 1
        else:
            Module.low_pulse_count += 1
        pulse = self._get_pulse_output(pulse_input, input_module)
        if pulse is not None:
            return [(output, pulse, self) for output in self.outputs]
        return []

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def print_conns(self) -> None:
        for output in self.outputs:
            print(f"{self.name} -> {output.name}")
            output.print_conns()


class Sink(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.state = False

    def _get_pulse_output(self, pulse_input: bool, input_module: 'Module') -> Optional[bool]:
        if not pulse_input:
            self.state = True
        return None


class FlipFlop(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.state = False

    def _get_pulse_output(self, pulse_input: bool, input_module: 'Module') -> Optional[bool]:
        if pulse_input:
            return None
        self.state = not self.state
        return self.state


class Conjunction(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.state = {}

    def add_input(self, input: 'Module') -> None:
        super().add_input(input)
        self.state[input] = False

    def _get_pulse_output(self, pulse_input: bool, input_module: 'Module') -> Optional[bool]:
        self.state[input_module] = pulse_input
        pulse = not all(self.state.values())
        if self.name in ["sx", "jt", "kb", "ks"]:
            print(f"{global_state}: {self.name} {pulse}")
        return pulse


class Broadcaster(Module):
    def __init__(self, name: str):
        super().__init__(name)

    def _get_pulse_output(self, pulse_input: bool, input_module: 'Module') -> Optional[bool]:
        return pulse_input


def build_module_graph(module_specs: [(str, str, [str])]) -> (Module, Module):
    defs = {}
    outputs = {}
    for spec in module_specs:
        tp, name, outs = spec
        if tp == "broadcaster":
            module = Broadcaster(name)
        elif tp == "%":
            module = FlipFlop(name)
        else:
            assert tp == "&"
            module = Conjunction(name)
        defs[name] = module
        outputs[name] = outs

    for name, outputs in outputs.items():
        src_mod = defs[name]
        out_mods = []
        for out in outputs:
            # Use base module as sink
            if out not in defs:
                defs[out] = Sink(out)
            out_mods.append(defs[out])
        src_mod.outputs = out_mods
        for module in out_mods:
            module.add_input(src_mod)

    return defs["broadcaster"], defs["rx"]


def read_inputs(filename: str) -> [(str, str, [str])]:
    with open(filename) as f:
        lines = [l.strip() for l in f.readlines()]

    module_specs = []
    for line in lines:
        src, dst = line.split(" -> ")
        if src == "broadcaster":
            tp = "broadcaster"
            name = "broadcaster"
        else:
            tp = src[0]
            name = src[1:]

        outputs = dst.split(", ")

        module_specs.append((tp, name, outputs))

    return module_specs


def simulate(module: Module, pulse: bool, input_module: Optional[Module] = None) -> None:
    queue = deque()
    queue.append((module, pulse, input_module))
    while len(queue) > 0:
        module, pulse, input_module = queue.popleft()
        pstr = "high" if pulse else "low"
        input_name = input_module.name if input_module is not None else "button"
        input_type = input_module.__class__.__name__ if input_module is not None else ""
        # print(f"{input_name} -{pstr}-> {module.name}")
        queue.extend(module(pulse, input_module))


def part1(filename: str) -> int:
    module_specs = read_inputs(filename)
    broadcaster, rx = build_module_graph(module_specs)
    # broadcaster.print_conns()
    for i in range(1000):
        simulate(broadcaster, False)
        print(i)
    return Module.low_pulse_count * Module.high_pulse_count


def part2(filename: str) -> int:
    global global_state
    module_specs = read_inputs(filename)
    broadcaster, rx = build_module_graph(module_specs)
    # broadcaster.print_conns()
    for i in range(20000):#itertools.count(start=1)
        global_state = i
        simulate(broadcaster, False)
        if rx.state:
            return i


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")

# sx = 3876, 7753, 11630, 15507, 19384
# 3877, 3877, 3877, 3877
# jt = 4048, 8097, 12146, 16195
# 4049, 4049, 4049
# kb = 3850, 7701, 11552, 15403, 19254
# 3851, 3851, 3851, 3851
# ks = 4020, 8041, 12062, 16083
# 4021, 4021, 4021
-1 + lcm of 3877, 4049, 3851, 4021
lcm = 243081086866483


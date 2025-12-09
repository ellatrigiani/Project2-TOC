from src.helpers.turing_machine import TuringMachineSimulator

#constants from helper
BLANK = "_"
WILDCARD = "*"
DIR_L = "L"
DIR_R = "R"
DIR_S = "S"


class NTM_Tracer(TuringMachineSimulator):
    def step(self, left, right, symbol_write, move_in):
        """
        Applying one transition to a single configuration.
        left is the string to the left of the head
        right is the symbol under the head and whatever is the remaining to the right
        """
        #tail is everything to the right of the current head 
        if right:
            tail = right[1:] #meaning head is right[0] and tail is everything else 
        else:
            tail = ""

        new_head = symbol_write

        if move_in == DIR_R:
            #moving right and leave written symbol behind on the left, head moves to next
            left_update = left + new_head
            right_update = tail  #if tail is empty it will read blank
        elif move_in == DIR_L:
            #move left meaning head moves to prev cell
            if left:
                moved_to = left[-1]
                left_update = left[:-1]
            else:
                moved_to = BLANK
                left_update = ""
            #new head is moved_to
            right_update = moved_to + new_head + tail
        elif move_in == DIR_S:
            left_update = left
            right_update = new_head + tail
        else:
            #extra test case that shouldn't be hit on machines that work
            left_update = left
            right_update = right

        return left_update, right_update

    def run(self, input_string, max_depth):
        """Breadth-first search of the NTM configuration tree."""
        print(f"Tracing NTM: {self.machine_name} on input '{input_string}'")

        #checking if input string is empty
        if input_string != "":
            tape = input_string
        else:
            tape = BLANK

        # Initial Configuration: ["", start_state, input_string]
        # Note: Represent configuration as triples (left, state, right) [cite: 156]
        initial_config = ["", self.start_state, tape] #modified to use my check values from above

         # The tree is a list of lists of configurations
        tree = [[initial_config]]

        #adding dictionary to track parent relationahips for path reconstruction
        parents = {tuple(initial_config): None} 

        depth = 0
        accepted = False

        while depth < max_depth and not accepted and tree[depth]: #added and tree[depth] to make sure current level exists 
            current_level = tree[depth]
            next_level = []
            all_rejected = True

            for config in current_level:
                left, state, right = config

                # Accepting state: done
                if state == self.accept_state:
                    print(f"String accepted in {depth} transitions.")
                    self.parents = parents
                    self.print_trace_path(config)
                    accepted = True
                    break

                #reject state handling to continue so we don't get stuck in infinite loop
                if state == self.reject_state:
                    continue

                #gets the symbol under head
                if right:
                    head_sym = right[0]
                else:
                    head_sym = BLANK

                #using helper method to get transitions
                transitions = self.get_transitions(state, (head_sym,))

                #no transitions is trap/reject so just continue
                if not transitions:
                    continue

                all_rejected = False

                #getting components from the dictionary
                for t in transitions:
                    next_state = t["next"]
                    symbol_write = t["write"][0]
                    move_in = t["move"][0]

                    #added wildcard handling if the symbol is *
                    if symbol_write == WILDCARD:
                        symbol_write = head_sym

                    #using my step method to apply transition
                    left_update, right_update = self.step(left, right, symbol_write, move_in)
                    
                    #creates new configuration and adds to nextlevel
                    child = [left_update, next_state, right_update]
                    next_level.append(child)

                    #tracks parent child relationships to reconstruct paths and avoids duplicates, need tuple values bc hashable
                    child_t = tuple(child)
                    parent_t = tuple(config)
                    if child_t not in parents:
                        parents[child_t] = parent_t

            if accepted:
                break

            #global rejection when all branches stop/halt
            if not next_level and all_rejected:
                print(f"String rejected in {depth} transitions.")
                break

            #moving to next depth level
            tree.append(next_level)
            depth += 1

        if depth >= max_depth and not accepted:
            print(f"Execution stopped after {max_depth} steps.")

    def print_trace_path(self, final_node):
        """Backtrack and print the path from start to the accepting node."""
        #initializing path to reconstruct
        parents = self.parents
        curr = tuple(final_node)
        path = []

        #going backwards through parent pointers
        while curr is not None:
            path.append(curr)
            curr = parents.get(curr)

        #reverse the path to get it in the correct order since we backtracked
        path.reverse()

        #format and print each config in the path
        print("Accepting path:")
        for (left, state, right) in path:
            head = right[0] if right else BLANK
            remaining = right[1:] if right else ""
            print(f"{left},{state},{head}{remaining}")

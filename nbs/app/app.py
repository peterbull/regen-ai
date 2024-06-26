# AUTOGENERATED! DO NOT EDIT! File to edit: ../240403_dspy_codegen.ipynb.

# %% auto 0
__all__ = ['phoenix_session', 'endpoint', 'resource', 'tracer_provider', 'span_otlp_exporter', 'tracer', 'llm', 'optimized_code',
           'GeneratePseudocode', 'PseudocodeToCode', 'CheckCodeCorrectness', 'RefinePseudocode',
           'RefineCodeWithPreviousContext', 'RefineTestsWithPreviousContext', 'GenerateTests',
           'IterativeCodeRefinement']

# %% ../240403_dspy_codegen.ipynb 1
# connect phoenix for tracing
import phoenix as px
phoenix_session = px.launch_app()

# %% ../240403_dspy_codegen.ipynb 2
from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# %% ../240403_dspy_codegen.ipynb 3
endpoint = "http://localhost:6006/v1/traces"
resource = Resource(attributes={})
tracer_provider = trace_sdk.TracerProvider(resource=resource)
span_otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter=span_otlp_exporter))

trace_api.set_tracer_provider(tracer_provider=tracer_provider)
DSPyInstrumentor().instrument()

# %% ../240403_dspy_codegen.ipynb 4
tracer = trace_api.get_tracer_provider().get_tracer(__name__)

# %% ../240403_dspy_codegen.ipynb 5
import subprocess
import dspy
import logging

class GeneratePseudocode(dspy.Signature):
    """
    Transform a high-level task description into pseudocode.
    """
    task = dspy.InputField(desc="High-level description of the task.")
    pseudocode = dspy.OutputField(desc="Generated pseudocode for the task.")

class PseudocodeToCode(dspy.Signature):
    """
    Convert pseudocode into executable code.
    """
    task = dspy.InputField(desc="High-level description of the task.")
    pseudocode = dspy.InputField(desc="Pseudocode for the task.")
    code = dspy.OutputField(desc="Executable code generated from pseudocode.")

class CheckCodeCorrectness(dspy.Signature):
    """
    Determine if the generated code meets the task requirements.
    """
    code = dspy.InputField(desc="The code to check.")
    tests = dspy.InputField(desc="Tests to run against the code.")
    code_execution_output = dspy.InputField(desc="The output of running the code.")
    correctness = dspy.OutputField(desc="Bool")

class RefinePseudocode(dspy.Signature):
    """
    Refine pseudocode based on the feedback from code execution and test results.
    """
    code_output = dspy.InputField(desc="Output produced by executing the code.")
    test_output = dspy.InputField(desc="Output produced by running the tests.")
    errors = dspy.InputField(desc="Errors encountered during code execution and testing.")
    new_pseudocode = dspy.OutputField(desc="Refined pseudocode.")

class RefineCodeWithPreviousContext(dspy.Signature):
    """
    Refine code by incorporating feedback and previous attempts.
    """
    task = dspy.InputField(desc="High-level description of the task.")
    new_pseudocode = dspy.InputField(desc="Newly refined pseudocode.")
    previous_code_errors = dspy.InputField(desc="Previous code and errors encountered.")
    new_code = dspy.OutputField(desc="Newly refined code.")

class RefineTestsWithPreviousContext(dspy.Signature):
    """
    Refine tests by incorporating feedback and previous attempts.
    """
    task = dspy.InputField(desc="High-level description of the task.")
    new_code = dspy.InputField(desc="Newly refined code.")
    previous_tests_errors = dspy.InputField(desc="Previous tests and errors encountered.")
    new_tests = dspy.OutputField(desc="Newly refined tests.")

class GenerateTests(dspy.Signature):
    """
    Generate tests for the given code.
    IMPORTANT: ONLY OUTPUT THE TESTS AS RAW PYTHON TEXT AND NOTHING ELSE!!
    """
    task = dspy.InputField(desc="the task that the code has been generated for.")
    code = dspy.InputField(desc="the code to generate tests for.")
    tests = dspy.OutputField(desc="the tests to run.")


class IterativeCodeRefinement(dspy.Module):
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        

        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        
        self.logger.info("Testing Log")

        self.generate_pseudocode = dspy.ChainOfThought(GeneratePseudocode)
        self.pseudocode_to_code = dspy.ChainOfThought(PseudocodeToCode)
        self.generate_code_tests = dspy.ChainOfThought(GenerateTests)
        self.check_code_correctness = dspy.ChainOfThought(CheckCodeCorrectness)
        self.refine_pseudocode = dspy.ChainOfThought(RefinePseudocode)
        self.refine_code_with_previous_context = dspy.ChainOfThought(RefineCodeWithPreviousContext)
        self.refine_tests_with_previous_context = dspy.ChainOfThought(RefineTestsWithPreviousContext)

    def execute_code(self, code):
        """
        Executes given Python code and captures the stdout, stderr, and return code.
        """
        result = subprocess.run(["python", "-c", code], capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode

    def forward(self, task):
        """
        Main method to iterate over code refinement based on task input.
        Refines the code up to 5 times if the desired correct code is not reached.
        """
        # Initial pseudocode and code generation
        pseudocode = self.generate_pseudocode(task=task).pseudocode
        code = self.pseudocode_to_code(task=task, pseudocode=pseudocode).code
        tests = self.generate_code_tests(task=task, code=code).tests

        # Log initial outputs
        self.logger.info(f"Generated pseudocode: {pseudocode}")
        self.logger.info(f"Generated code: {code}")
        self.logger.info(f"Generated tests: {tests}")
        
        # Initial code execution
        stdout, stderr, returncode = self.execute_code(code + "\n\n" + tests)
        is_correct = self.check_code_correctness(code=code, tests=tests, code_execution_output=stdout + stderr).correctness
        
        # Iterative refinement loop
        iteration_count = 0
        while not is_correct and iteration_count < 5:
            refinement_result = self.refine(task, stdout, stderr, returncode, is_correct)
            code, tests, stdout, stderr, is_correct = refinement_result.values()

            self.logger.info(f"Iteration {iteration_count+1}: refinement done with correctness: {is_correct}")

            if is_correct:
                break  # Exit loop if code is correct
            iteration_count += 1

        # Log final state
        self.logger.info(f"Final iteration count: {iteration_count}")
        self.logger.info(f"Final code: {code}")
        self.logger.info(f"Final tests: {tests}")
        self.logger.info(f"Final execution output: {stdout}")
        self.logger.info(f"Final execution errors: {stderr}")
        self.logger.info(f"Final correctness: {is_correct}")

        # Final return with refined code, tests, and execution results
        return {"final_code": code, "final_tests": tests, "output": stdout, "errors": stderr, "correctness": is_correct}
        
    @tracer.start_as_current_span("refine")
    def refine(self, task, stdout, stderr, returncode, is_correct):
        new_pseudocode = self.refine_pseudocode(code_output=stdout, test_output=stderr, errors=str(returncode)).new_pseudocode
        code = self.refine_code_with_previous_context(task=task, new_pseudocode=new_pseudocode, previous_code_errors=stderr).new_code
        tests = self.refine_tests_with_previous_context(task=task, new_code=code, previous_tests_errors=stderr).new_tests

        # Execute refined code
        stdout, stderr, returncode = self.execute_code(code + "\n\n" + tests)
        is_correct = bool(self.check_code_correctness(code=code, tests=tests, code_execution_output=stdout + stderr).correctness)

        # Log refinement iteration results
        self.logger.info(f"Refined pseudocode: {new_pseudocode}")
        self.logger.info(f"Refined code: {code}")
        self.logger.info(f"Refined tests: {tests}")
        self.logger.info(f"Execution output: {stdout}")
        self.logger.info(f"Is correct: {is_correct}")
        # Final return with refined code and tests
        return {
            "final_code": code,
            "final_tests": tests,
            "output": stdout,
            "errors": stderr,
            "correctness": is_correct
        }

# %% ../240403_dspy_codegen.ipynb 6
llm = dspy.OllamaLocal("open-hermes-2-4_0", max_tokens=3000, model_type="chat")
dspy.settings.configure(lm=llm)

# %% ../240403_dspy_codegen.ipynb 7
optimized_code = IterativeCodeRefinement()(task="Write a python script that takes a user input and returns a hash of that input.")
print(optimized_code)

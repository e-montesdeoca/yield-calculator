
from dataclasses import dataclass
from bakery import assert_equal
from drafter import *
import math

hide_debug_information()
set_website_title("Stoichiometry Calculator")
set_website_framed(False)
set_site_information(
    author="Emily Montesdeoca",
    description="An educational stoichiometry calculator that helps students identify limiting reactants, calculate theoretical and percent yield, and understand each step of the process. The website automatically calculates molar masses using a dictionary of atomic masses.",
    sources=[
        "https://drafter-edu.github.io/drafter/"
    ],
    planning=[],
    links=[]
)

ATOMIC_MASSES = {
    "H": 1.008,
    "He": 4.0026,
    "Li": 6.94,
    "Be": 9.0122,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Ne": 20.180,
    "Na": 22.990,
    "Mg": 24.305,
    "Al": 26.982,
    "Si": 28.085,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "Ar": 39.948,
    "K": 39.098,
    "Ca": 40.078,
    "Sc": 44.956,
    "Ti": 47.867,
    "V": 50.942,
    "Cr": 51.996,
    "Mn": 54.938,
    "Fe": 55.845,
    "Co": 58.933,
    "Ni": 58.693,
    "Cu": 63.546,
    "Zn": 65.38,
    "Ga": 69.723,
    "Ge": 72.630,
    "As": 74.922,
    "Se": 78.971,
    "Br": 79.904,
    "Kr": 83.798,
    "Rb": 85.468,
    "Sr": 87.62,
    "Ag": 107.8682,
    "Cd": 112.414,
    "Sn": 118.710,
    "I": 126.904,
    "Ba": 137.327,
    "Pt": 195.084,
    "Au": 196.967,
    "Hg": 200.592,
    "Pb": 207.2
}


@dataclass
class Reactant:
    chemical_formula: str
    coefficient: int
    molar_mass: float
    starting_mass: float


@dataclass
class State:
    balanced_equation: str
    selected_product: str
    actual_yield: float | None
    reactants: list[Reactant]
    product_coefficient: int
    product_molar_mass: float
    error_message: str = ""


def calculate_molar_mass(chemical_formula: str) -> float:
    """
    Calculate molar mass using a dictionary
    of atomic masses.
    """
    formula = chemical_formula.strip()

    if formula == "":
        raise ValueError("Enter a chemical formula.")

    totals = [0.0]
    group_has_content = [False]
    position = 0

    while position < len(formula):
        character = formula[position]

        if character == "(":
            totals.append(0.0)
            group_has_content.append(False)
            position += 1

        elif character == ")":
            if len(totals) == 1:
                raise ValueError("Invalid parentheses.")

            if group_has_content[-1] == False:
                raise ValueError("Empty parentheses.")

            group_mass = totals.pop()
            group_has_content.pop()
            position += 1

            number = ""

            while position < len(formula) and formula[position].isdigit():
                number += formula[position]
                position += 1

            multiplier = 1

            if number != "":
                multiplier = int(number)

            if multiplier <= 0:
                raise ValueError("Invalid atom count.")

            totals[-1] += group_mass * multiplier
            group_has_content[-1] = True

        elif character.isupper():
            element = character
            position += 1

            if position < len(formula) and formula[position].islower():
                element += formula[position]
                position += 1

            if element not in ATOMIC_MASSES:
                raise ValueError("Unknown element: " + element)

            number = ""

            while position < len(formula) and formula[position].isdigit():
                number += formula[position]
                position += 1

            multiplier = 1

            if number != "":
                multiplier = int(number)

            if multiplier <= 0:
                raise ValueError("Invalid atom count.")

            totals[-1] += ATOMIC_MASSES[element] * multiplier
            group_has_content[-1] = True

        else:
            raise ValueError("Invalid chemical formula.")

    if len(totals) != 1:
        raise ValueError("Missing closing parenthesis.")

    return totals[0]


def calculate_possible_yield(
    reactant: Reactant,
    product_coefficient: int,
    product_molar_mass: float
) -> float:
    """
    Calculate the amount of product one
    reactant can produce.
    """
    reactant_moles = reactant.starting_mass / reactant.molar_mass

    product_moles = (
        reactant_moles / reactant.coefficient
    ) * product_coefficient

    possible_yield = product_moles * product_molar_mass

    return possible_yield


def calculate_theoretical_yield(state: State) -> float:
    """
    Find the smallest possible yield
    from all reactants.
    """
    if len(state.reactants) == 0:
        return 0.0

    possible_yields = []

    for reactant in state.reactants:
        possible_yield = calculate_possible_yield(
            reactant,
            state.product_coefficient,
            state.product_molar_mass
        )

        possible_yields.append(possible_yield)

    return min(possible_yields)


def calculate_limiting_reactant(state: State) -> str:
    """
    Find which reactant produces the
    smallest amount of product.
    """
    if len(state.reactants) == 0:
        return ""

    limiting_reactant = ""
    smallest_yield = float("inf")

    for reactant in state.reactants:
        possible_yield = calculate_possible_yield(
            reactant,
            state.product_coefficient,
            state.product_molar_mass
        )

        if possible_yield < smallest_yield:
            smallest_yield = possible_yield
            limiting_reactant = reactant.chemical_formula

    return limiting_reactant


def calculate_percent_yield(state: State) -> float | None:
    """
    Calculate percent yield when actual
    yield is provided.
    """
    if state.actual_yield is None:
        return None

    theoretical_yield = calculate_theoretical_yield(state)

    if theoretical_yield <= 0:
        return None

    percent_yield = (
        state.actual_yield / theoretical_yield
    ) * 100

    return percent_yield


def validate_calculation(state: State) -> str:
    """
    Check that the information entered
    can be used for calculations.
    """
    if len(state.reactants) == 0:
        return "Please add at least one reactant."

    if state.selected_product == "":
        return "Please enter a product."

    if state.product_coefficient <= 0:
        return "Product coefficient must be positive."

    if state.product_molar_mass <= 0:
        return "Product molar mass must be positive."

    if state.actual_yield is not None:
        if not math.isfinite(state.actual_yield):
            return "Actual yield must be a valid number."

        if state.actual_yield < 0:
            return "Actual yield cannot be negative."

    for reactant in state.reactants:
        if reactant.coefficient <= 0:
            return "Reactant coefficients must be positive."

        if reactant.molar_mass <= 0:
            return "Reactant molar masses must be positive."

        if not math.isfinite(reactant.starting_mass):
            return "Starting masses must be valid numbers."

        if reactant.starting_mass < 0:
            return "Starting masses cannot be negative."

    theoretical_yield = calculate_theoretical_yield(state)

    if theoretical_yield <= 0:
        return "Theoretical yield must be greater than zero."

    return ""


assert_equal(round(calculate_molar_mass("H2O"), 2), 18.02)
assert_equal(round(calculate_molar_mass("H2"), 2), 2.02)
assert_equal(round(calculate_molar_mass("Ca(OH)2"), 3), 74.092)
assert_equal(round(calculate_molar_mass("Al2(SO4)3"), 3), 342.132)

test_hydrogen = Reactant("H2", 2, 2.016, 4.032)
test_oxygen = Reactant("O2", 1, 32.00, 16.00)

test_state = State(
    "2H2 + O2 -> 2H2O",
    "H2O",
    15.0,
    [test_hydrogen, test_oxygen],
    2,
    18.015
)

assert_equal(
    round(calculate_possible_yield(test_hydrogen, 2, 18.015), 3),
    36.03
)

assert_equal(
    round(calculate_possible_yield(test_oxygen, 2, 18.015), 3),
    18.015
)

assert_equal(
    calculate_theoretical_yield(test_state),
    18.015
)

assert_equal(
    calculate_limiting_reactant(test_state),
    "O2"
)

assert_equal(
    round(calculate_percent_yield(test_state), 2),
    83.26
)

test_without_actual = State(
    "2H2 + O2 -> 2H2O",
    "H2O",
    None,
    [test_hydrogen, test_oxygen],
    2,
    18.015
)

assert_equal(
    calculate_percent_yield(test_without_actual),
    None
)

test_three = State(
    "",
    "P",
    None,
    [
        Reactant("A", 1, 10.0, 10.0),
        Reactant("B", 1, 10.0, 5.0),
        Reactant("C", 1, 10.0, 20.0)
    ],
    1,
    10.0
)

assert_equal(
    calculate_limiting_reactant(test_three),
    "B"
)

assert_equal(
    calculate_theoretical_yield(test_three),
    5.0
)

test_empty = State("", "", None, [], 0, 0.0)

assert_equal(
    calculate_theoretical_yield(test_empty),
    0.0
)

assert_equal(
    calculate_limiting_reactant(test_empty),
    ""
)


@route
def index(state: State) -> Page:
    """
    Display the homepage.
    """
    return Page(state, [
        Header("Stoichiometry Calculator"),

        Text(
            "Calculate limiting reactants, "
            "theoretical yield, and percent yield."
        ),

        Text(
            "Molar masses are calculated automatically "
            "using chemical formulas."
        ),

        Button("Start Calculating", input_reaction),
        Button("Learn Concepts", learn_concepts)
    ])


def display_reactants(state: State) -> list:
    """
    Display all reactants entered
    by the student.
    """
    reactant_display = []

    for reactant in state.reactants:
        reactant_display.append(
            Text(
                reactant.chemical_formula +
                " | Coefficient: " +
                str(reactant.coefficient) +
                " | Molar Mass: " +
                str(round(reactant.molar_mass, 3)) +
                " g/mol | Starting Mass: " +
                str(reactant.starting_mass) + " g"
            )
        )

    return reactant_display


@route
def input_reaction(state: State) -> Page:
    """
    Display the reaction input page.
    """
    if state.actual_yield is None:
        actual_yield_text = ""
    else:
        actual_yield_text = str(state.actual_yield)

    return Page(state, [
        Header("Enter Your Reaction"),

        Text(state.error_message),

        Header("Balanced Chemical Equation"),

        Text(
            "Enter a balanced equation. "
            "For example: 2H2 + O2 -> 2H2O."
        ),

        Text(
            "Enter the coefficients separately below."
        ),

        TextBox(
            "balanced_equation",
            state.balanced_equation
        ),

        Button("Save Equation", save_reaction),

        Header("Add a Reactant"),

        Text(
            "Enter ONE reactant at a time. "
            "Include its formula, coefficient, and "
            "starting mass. Click Add Reactant "
            "after each entry."
        ),

        Text("Chemical Formula"),
        TextBox("chemical_formula"),

        Text("Coefficient"),
        TextBox("coefficient"),

        Text("Starting Mass (g)"),
        TextBox("starting_mass"),

        Button("Add Reactant", add_reactant),

        Header("Your Reactants")

    ] + display_reactants(state) + [

        Header("Product Information"),

        Text("Selected Product"),
        TextBox(
            "selected_product",
            state.selected_product
        ),

        Text("Product Coefficient"),
        TextBox(
            "product_coefficient",
            str(state.product_coefficient)
        ),

        Text("Actual Yield (g) - Optional"),

        Text(
            "Leave blank if actual yield "
            "is not provided."
        ),

        TextBox(
            "actual_yield",
            actual_yield_text
        ),

        Button("Save Product", save_product),

        Button("Calculate Results", show_results),

        Button("Back to Home", index)
    ])


@route
def save_reaction(
    state: State,
    balanced_equation: str
) -> Page:
    """
    Save the balanced equation.
    """
    state.balanced_equation = balanced_equation
    state.error_message = ""

    return input_reaction(state)


@route
def add_reactant(
    state: State,
    chemical_formula: str,
    coefficient: str,
    starting_mass: str
) -> Page:
    """
    Add a reactant to the list and
    calculate its molar mass.
    """
    try:
        formula = chemical_formula.strip()
        coefficient_number = int(coefficient)
        starting_mass_number = float(starting_mass)

        molar_mass = calculate_molar_mass(formula)

        if coefficient_number <= 0:
            state.error_message = (
                "Coefficient must be positive."
            )

        elif not math.isfinite(starting_mass_number):
            state.error_message = (
                "Starting mass must be a valid number."
            )

        elif starting_mass_number < 0:
            state.error_message = (
                "Starting mass cannot be negative."
            )

        else:
            new_reactant = Reactant(
                formula,
                coefficient_number,
                molar_mass,
                starting_mass_number
            )

            state.reactants.append(new_reactant)
            state.error_message = ""

    except (ValueError, TypeError, KeyError) as error:
        state.error_message = str(error)

    return input_reaction(state)


@route
def save_product(
    state: State,
    selected_product: str,
    product_coefficient: str,
    actual_yield: str
) -> Page:
    """
    Save product information and
    calculate its molar mass.
    """
    try:
        formula = selected_product.strip()
        coefficient = int(product_coefficient)

        if actual_yield.strip() == "":
            yield_amount = None
        else:
            yield_amount = float(actual_yield)

        molar_mass = calculate_molar_mass(formula)

        if coefficient <= 0:
            state.error_message = (
                "Product coefficient must be positive."
            )

        elif yield_amount is not None and (
            not math.isfinite(yield_amount) or yield_amount < 0
        ):
            state.error_message = (
                "Actual yield must be a nonnegative number."
            )

        else:
            state.selected_product = formula
            state.product_coefficient = coefficient
            state.product_molar_mass = molar_mass
            state.actual_yield = yield_amount
            state.error_message = ""

    except (ValueError, TypeError, KeyError) as error:
        state.error_message = str(error)

    return input_reaction(state)


@route
def show_results(state: State) -> Page:
    """
    Display the results of the
    stoichiometry calculations.
    """
    error = validate_calculation(state)

    if error != "":
        state.error_message = error
        return input_reaction(state)

    state.error_message = ""

    limiting_reactant = calculate_limiting_reactant(state)
    theoretical_yield = calculate_theoretical_yield(state)
    percent_yield = calculate_percent_yield(state)

    results = [
        Header("Calculation Results"),

        Header("Limiting Reactant"),
        Text(limiting_reactant),

        Header("Theoretical Yield"),
        Text(str(round(theoretical_yield, 2)) + " g")
    ]

    if percent_yield is not None:
        results.append(Header("Actual Yield"))
        results.append(Text(str(state.actual_yield) + " g"))

        results.append(Header("Percent Yield"))
        results.append(Text(str(round(percent_yield, 2)) + "%"))

    else:
        results.append(
            Text(
                "Percent yield was not calculated "
                "because no actual yield was provided."
            )
        )

    results.append(
        Button("View Step-by-Step Explanation", show_steps)
    )

    results.append(
        Button("Back to Reaction", input_reaction)
    )

    results.append(
        Button("Try Another Reaction", reset_calculator)
    )

    return Page(state, results)


@route
def show_steps(state: State) -> Page:
    """
    Explain how each calculation
    was completed.
    """
    error = validate_calculation(state)

    if error != "":
        state.error_message = error
        return input_reaction(state)

    steps = [
        Header("Step-by-Step Explanation"),
        Header("Step 1: Convert Reactants to Moles")
    ]

    for reactant in state.reactants:
        moles = (
            reactant.starting_mass / reactant.molar_mass
        )

        product_moles = (
            moles / reactant.coefficient
        ) * state.product_coefficient

        possible_yield = (
            product_moles * state.product_molar_mass
        )

        steps.append(
            Text(
                reactant.chemical_formula + ": " +
                str(reactant.starting_mass) + " g / " +
                str(round(reactant.molar_mass, 3)) +
                " g/mol = " +
                str(round(moles, 4)) + " mol"
            )
        )

        steps.append(
            Text(
                "Possible product from " +
                reactant.chemical_formula + ": " +
                str(round(moles, 4)) + " mol x (" +
                str(state.product_coefficient) + "/" +
                str(reactant.coefficient) + ") x " +
                str(round(state.product_molar_mass, 3)) +
                " g/mol = " +
                str(round(possible_yield, 2)) + " g"
            )
        )

    theoretical_yield = calculate_theoretical_yield(state)
    limiting_reactant = calculate_limiting_reactant(state)

    steps.append(
        Header("Step 2: Identify the Limiting Reactant")
    )

    steps.append(
        Text(
            limiting_reactant +
            " produces the smallest amount of product."
        )
    )

    steps.append(
        Header("Step 3: Determine Theoretical Yield")
    )

    steps.append(
        Text(
            str(round(theoretical_yield, 2)) + " g"
        )
    )

    percent_yield = calculate_percent_yield(state)

    if percent_yield is not None:
        steps.append(
            Header("Step 4: Calculate Percent Yield")
        )

        steps.append(
            Text(
                "Percent Yield = "
                "(Actual Yield / Theoretical Yield) x 100"
            )
        )

        steps.append(
            Text(
                str(state.actual_yield) + " / " +
                str(round(theoretical_yield, 2)) +
                " x 100 = " +
                str(round(percent_yield, 2)) + "%"
            )
        )

    else:
        steps.append(Header("Step 4: Percent Yield"))

        steps.append(
            Text(
                "Percent yield cannot be calculated "
                "without an actual yield."
            )
        )

    steps.append(
        Button("Back to Results", show_results)
    )

    return Page(state, steps)


@route
def learn_concepts(state: State) -> Page:
    """
    Explain important stoichiometry
    concepts to the student.
    """
    return Page(state, [
        Header("Learn Stoichiometry"),

        Header("Limiting Reactant"),
        Text(
            "The reactant that runs out first "
            "and limits the amount of product formed."
        ),

        Header("Theoretical Yield"),
        Text(
            "The maximum amount of product "
            "predicted by stoichiometry."
        ),

        Header("Actual Yield"),
        Text(
            "The amount of product actually "
            "obtained in an experiment."
        ),

        Header("Percent Yield"),
        Text(
            "(Actual Yield / Theoretical Yield) x 100"
        ),

        Header("How to Solve Stoichiometry Problems"),

        Text("1. Start with a balanced equation."),
        Text("2. Convert reactant masses to moles."),
        Text("3. Use coefficients as mole ratios."),
        Text("4. Calculate possible product masses."),
        Text("5. Identify the limiting reactant."),
        Text("6. Calculate theoretical yield."),
        Text("7. Calculate percent yield if possible."),

        Button("Back to Home", index),
        Button("Start Calculating", input_reaction)
    ])


@route
def reset_calculator(state: State) -> Page:
    """
    Clear the reaction information
    so the student can start again.
    """
    state.balanced_equation = ""
    state.selected_product = ""
    state.actual_yield = None
    state.reactants = []
    state.product_coefficient = 0
    state.product_molar_mass = 0.0
    state.error_message = ""

    return input_reaction(state)


initial_state = State(
    "",
    "",
    None,
    [],
    0,
    0.0
)

start_server(initial_state)



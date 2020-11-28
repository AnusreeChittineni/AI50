import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Initializes a variable to store the joint probability
    # Sets value to 1 because a value of one will not affect further calculations
    joint_prob = 1

    # Initializes an empty set to store everyone with zero copies of the gene
    zero_genes = set()

    # Initializes an empty set to store everyone who does not have the trait
    no_trait = set()

    # Loops through each person in people
    for person in people.keys():

        # If the person is not found in either one_gene or two_genes...
        if person not in one_gene and person not in two_genes:

            # ...add person to zero_genes
            zero_genes.add(person)

        # If the person is not found in have_trait...
        if person not in have_trait:

            # ...add person to no_trait
            no_trait.add(person)

    # Loops through each person in zero_genes and calculates the probability of the person having zero copies of the gene and their current trait state
    for person in zero_genes:

        # Checks if the person has a mother listed in the data
        if people[person]["mother"] == None:

            # If not, then use the preset values to calculate the probability because the probability is not conditional
            probability = PROBS["gene"][0]

        # Otherwise...
        else:

            # Initialize a varaible to store the probability
            # Sets value to 1 beacuse a value of one will not affect further calculations
            probability = 1

            # Get person's parents from data
            mother = people[person]["mother"]

            father = people[person]["father"]

            # Check the state of the mother and father's gene counts
            # If statement returns true, then multiply the current probability by the expression below the if statement
            # Each expression represents the probability of the person having zero copies of the gene based on their parent's gene counts
            if mother in zero_genes and father in zero_genes:

                probability *= (1-PROBS["mutation"]) ** 2

            elif mother in one_gene and father in one_gene:

                probability *= 0.5 ** 2

            elif mother in two_genes and father in two_genes:

                probability *= (PROBS["mutation"]) ** 2

            elif (mother in zero_genes and father in one_gene) or (mother in one_gene and father in zero_genes):

                probability *= (1-PROBS["mutation"]) * 0.5

            elif (mother in zero_genes and father in two_genes) or (mother in two_genes and father in zero_genes):

                probability *= (1-PROBS["mutation"]) * (PROBS["mutation"])

            elif (mother in one_gene and father in two_genes) or (mother in two_genes and father in one_gene):

                probability *= 0.5 * (PROBS["mutation"])

        # Checks if the person has the trait or not
        # If the statement returns true, then multiply the current probability by the probability of the person having that trait state with a gene count of 0
        if person in no_trait:

            probability *= PROBS["trait"][0][False]

        elif person in have_trait:

            probability *= PROBS["trait"][0][True]

        # Multiply current joint probability with the final probability for the current person
        joint_prob *= probability

    # Loops through each person in one_gene and calculates the probability of the person having one copy of the gene and their current trait state
    for person in one_gene:

        # Checks if the person has a mother listed in the data
        if people[person]["mother"] == None:

            # If not, then use the preset values to calculate the probability because the probability is not conditional
            probability = PROBS["gene"][1]

        # Otherwise...
        else:

            # Initialize a varaible to store the probability
            # Sets value to 1 beacuse a value of one will not affect further calculations
            probability = 1

            # Get person's parents from data
            mother = people[person]["mother"]

            father = people[person]["father"]

            # Check the state of the mother and father's gene counts
            # If statement returns true, then multiply the current probability by the expression below the if statement
            # Each expression represents the probability of the person having one copy of the gene based on their parent's gene counts
            if mother in zero_genes and father in zero_genes:

                probability *= ((1-PROBS["mutation"]) * (PROBS["mutation"])) * 2

            elif mother in one_gene and father in one_gene:

                probability *= (0.5 * 0.5) * 2

            elif mother in two_genes and father in two_genes:

                probability *= ((1-PROBS["mutation"]) * (PROBS["mutation"])) * 2

            elif (mother in zero_genes and father in one_gene) or (mother in one_gene and father in zero_genes):

                probability *= ((1-PROBS["mutation"]) * 0.5) + ((PROBS["mutation"]) * 0.5)

            elif (mother in zero_genes and father in two_genes) or (mother in two_genes and father in zero_genes):

                probability *= ((1-PROBS["mutation"]) ** 2) + ((PROBS["mutation"]) ** 2)

            elif (mother in one_gene and father in two_genes) or (mother in two_genes and father in one_gene):

                probability *= (0.5 * (PROBS["mutation"])) + (0.5 * (1-PROBS["mutation"]))

        # Checks if the person has the trait or not
        # If the statement returns true, then multiply the current probability by the probability of the person having that trait state with a gene count of 1
        if person in no_trait:

            probability *= PROBS["trait"][1][False]

        elif person in have_trait:

            probability *= PROBS["trait"][1][True]

        # Multiply current joint probability with the final probability for the current person
        joint_prob *= probability

    # Loops through each person in two_genes and calculates the probability of the person having two copies of the gene and their current trait state
    for person in two_genes:

        # Checks if the person has a mother listed in the data
        if people[person]["mother"] == None:

            # If not, then use the preset values to calculate the probability because the probability is not conditional
            probability = PROBS["gene"][2]

        # Otherwise...
        else:

            # Initialize a varaible to store the probability
            # Sets value to 1 beacuse a value of one will not affect further calculations
            probability = 1

            # Get person's parents from data
            mother = people[person]["mother"]

            father = people[person]["father"]

            # Check the state of the mother and father's gene counts
            # If statement returns true, then multiply the current probability by the expression below the if statement
            # Each expression represents the probability of the person having two copies of the gene based on their parent's gene counts
            if mother in zero_genes and father in zero_genes:

                probability *= (PROBS["mutation"]) ** 2

            elif mother in one_gene and father in one_gene:

                probability *= 0.5 * 0.5

            elif mother in two_genes and father in two_genes:

                probability *= (1-PROBS["mutation"]) ** 2

            elif (mother in zero_genes and father in one_gene) or (mother in one_gene and father in zero_genes):

                probability *= (PROBS["mutation"]) * 0.5

            elif (mother in zero_genes and father in two_genes) or (mother in two_genes and father in zero_genes):

                probability *= (PROBS["mutation"]) * (1-PROBS["mutation"])

            elif (mother in one_gene and father in two_genes) or (mother in two_genes and father in one_gene):

                probability *= 0.5 * (1-PROBS["mutation"])

        # Checks if the person has the trait or not
        # If the statement returns true, then multiply the current probability by the probability of the person having that trait state with a gene count of 2
        if person in no_trait:

            probability *= PROBS["trait"][2][False]

        elif person in have_trait:

            probability *= PROBS["trait"][2][True]

        # Multiply current joint probability with the final probability for the current person
        joint_prob *= probability

    # Return final value of joint probability
    return joint_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # Initializes an empty set to store everyone with zero copies of the gene
    zero_genes = set()

    # Initializes an empty set to store everyone who does not have the trait
    no_trait = set()

    # Loops through each person in people
    for person in probabilities.keys():

        # If the person is not found in either one_gene or two_genes...
        if person not in one_gene and person not in two_genes:

            # ...add person to zero_genes
            zero_genes.add(person)

        # If the person is not found in have_trait...
        if person not in have_trait:

            # ...add person to no_trait
            no_trait.add(person)

    # Loops through each person in the set for every set, adding p to the corresponding value in the probabilities dictionary
    for person in zero_genes:

        probabilities[person]["gene"][0] += p

    for person in one_gene:

        probabilities[person]["gene"][1] += p

    for person in two_genes:

        probabilities[person]["gene"][2] += p

    for person in no_trait:

        probabilities[person]["trait"][False] += p

    for person in have_trait:

        probabilities[person]["trait"][True] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    # Loops through each person in probabilities
    for person in probabilities:

        # Calculate the normalization factors for current person by summing up all the values under each key
        normalization_factor_gene = sum(probabilities[person]["gene"].values())

        normalization_factor_trait = sum(probabilities[person]["trait"].values())

        # Loop through each gene count for current person and divide the stored value by the corresponding normaliztion factor
        for gene in probabilities[person]["gene"].keys():

            probabilities[person]["gene"][gene] /= normalization_factor_gene

        # Loop through each trait state for current person and divide the stored value by the corresponding normaliztion factor
        for trait in probabilities[person]["trait"].keys():

            probabilities[person]["trait"][trait] /= normalization_factor_trait


if __name__ == "__main__":
    main()

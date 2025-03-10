import argparse
import json

from pydantic import TypeAdapter

from app.routers.generate import generate_model
from app.routers.model import get_config, get_valves
from app.support.base_models import ModelData, Valves


def main():
    parser = argparse.ArgumentParser(
        prog="PeriHub model generator script",
        description="Generate a PeriHub model based on the provided configuration.",
    )
    parser.add_argument("modelname")
    args = parser.parse_args()

    model_dict = get_config(args.modelname)
    model = TypeAdapter(ModelData).validate_json(json.dumps(model_dict))
    valves_dict = get_valves(args.modelname)
    valves = TypeAdapter(Valves).validate_json(json.dumps(valves_dict))
    generate_model(model, valves, args.modelname)


if __name__ == "__main__":
    main()

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import i2c
from esphome.const import (
    CONF_ID,
    CONF_INPUT,
    CONF_NUMBER,
    CONF_MODE,
    CONF_INVERTED,
    CONF_OUTPUT,
)

DEPENDENCIES = ["i2c"]
MULTI_CONF = False

pca9555_ns = cg.esphome_ns.namespace("pca9555")

PCA9555Component = pca9555_ns.class_("PCA9555Component", cg.Component, i2c.I2CDevice)
PCA9555GPIOPin = pca9555_ns.class_("PCA9555GPIOPin", cg.GPIOPin)

CONF_PCA9555 = "pca9555"
CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.declare_id(PCA9555Component)
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(i2c.i2c_device_schema(0x20)) #Note: 0x20 for the non-A part. The PCA9555A parts start at addess 0x38
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)


def validate_mode(value):
    if not (value[CONF_INPUT] or value[CONF_OUTPUT]):
        raise cv.Invalid("Mode must be either input or output")
    if value[CONF_INPUT] and value[CONF_OUTPUT]:
        raise cv.Invalid("Mode must be either input or output")
    return value


PCA9554_PIN_SCHEMA = cv.All(
    {
        cv.GenerateID(): cv.declare_id(PCA9555GPIOPin),
        cv.Required(CONF_PCA9555): cv.use_id(PCA9555Component),
        cv.Required(CONF_NUMBER): cv.int_range(min=0, max=8),
        cv.Optional(CONF_MODE, default={}): cv.All(
            {
                cv.Optional(CONF_INPUT, default=False): cv.boolean,
                cv.Optional(CONF_OUTPUT, default=False): cv.boolean,
            },
            validate_mode,
        ),
        cv.Optional(CONF_INVERTED, default=False): cv.boolean,
    }
)


@pins.PIN_SCHEMA_REGISTRY.register("pca9555", PCA9554_PIN_SCHEMA)
async def pca9555_pin_to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    parent = await cg.get_variable(config[CONF_PCA9554])

    cg.add(var.set_parent(parent))

    num = config[CONF_NUMBER]
    cg.add(var.set_pin(num))
    cg.add(var.set_inverted(config[CONF_INVERTED]))
    cg.add(var.set_flags(pins.gpio_flags_expr(config[CONF_MODE])))
    return var

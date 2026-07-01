# Makefile — convenience targets for the pool-room Blender project.

REPO := $(shell pwd)
DRIVERS_DIR := $(REPO)/drivers
RENDERS_DIR := $(REPO)/renders
BLENDER := $(if $(BLENDER_BIN),$(BLENDER_BIN),/tmp/blender-4.2.3-linux-x64/blender)

.PHONY: help list check topdown sw_hi ee_wide ns_ew all clean-stage

help:
	@echo "Available targets:"
	@echo "  make list         - list driver scripts"
	@echo "  make check        - syntax-check both build modules"
	@echo "  make topdown      - render top-down"
	@echo "  make sw_hi        - render SW-corner high-res 11mm"
	@echo "  make ee_wide      - render Emergency Exit 14mm wide-angle"
	@echo "  make ns_ew        - render N-strip E->W"
	@echo "  make all          - render every driver in drivers/"
	@echo "  make clean-stage  - remove staged copies in /tmp/blender_test/"

list:
	@./render.sh list

check:
	@python3 -c "import ast; ast.parse(open('build_pool_room.py').read()); print('build_pool_room.py OK')"
	@python3 -c "import ast; ast.parse(open('build_pool_room_furniture.py').read()); print('build_pool_room_furniture.py OK')"

topdown:
	@./render.sh test_driver_v15b_topdown

sw_hi:
	@./render.sh test_driver_v15L_persp_sw_hi

ee_wide:
	@./render.sh test_driver_v15L_persp_ee

ns_ew:
	@./render.sh test_driver_v15L_persp_ns

all:
	@./render.sh all

clean-stage:
	@rm -rf /tmp/blender_test/*.py /tmp/blender_test/*.png
	@echo "cleaned staging dir"

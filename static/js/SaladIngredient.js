var SaladIngredient = function(saladManager, data) {
    var self = this;

    self.saladManager = saladManager;
    self.data = data;

    self.id = data.id;
    self.name = data.name;

    self.lcNames = data.lower_category_names;
    self.ldNames = data.lower_direct_names;
    self.ucNames = data.upper_category_names;
    self.udNames = data.upper_direct_names;
    self.lNames = data.lower_names;
    self.uNames = data.upper_names;
    self.aNames = data.all_names;

    self.lClashNames = data.lower_clashes_with_names;
    self.uClashNames = data.upper_clashes_with_names;
    self.aClashNames = data.all_clashes_with_names;

    self.prevPresent = false;
    self.present = false;

    self.prevSelected = false;
    self.selected = false;

    self.prevLocked = false;
    self.locked = false;

    self.prevConnected = false;
    self.connected = false;

    self.prevMenu = false;
    self.menu = false;

    self.prevHighlighted = false;
    self.highlighted = false;

    if (data.salad_green == 'y') {
        self.color = 'lightgreen';
    } else if (data.salad_extra == 'y') {
        if (data.veg == 'y') {
            self.color = 'green';
        } else if (data.fruit == 'y') {
            self.color = 'orange';
        } else if (data.protein_nut_seed == 'y') {
            self.color = 'brown';
        } else {
            self.color = 'lightgrey';
        }
    } else if (data.salad_dressing == 'y') {
        self.color = 'tan';
    } else {
        self.color = 'black';
    }

    self.renderConnection = function(otherName, connectionType) {
        var other = self.saladManager.getFromName(otherName);
        var edgeId;
        var fromId;
        var toId;
        if (self.id > other.id) {
            edgeId = other.id.toString() + '-' + self.id.toString();
            fromId = other.name;
            toId = self.name;
        } else {
            edgeId = self.id.toString() + '-' + other.id.toString();
            fromId = self.name;
            toId = other.name;
        }

        var edgeColor;
        var physics;
        var hidden;
        if (connectionType == 'ud') {
            edgeColor = 'black';
            physics = true;
            hidden = false;
        } else if (connectionType == 'uc') {
            edgeColor = 'lightgrey';
            physics = true;
            hidden = false;
        } else if (connectionType == 'ld') {
            edgeColor = 'whitesmoke';
            physics = self.selected && other.selected;
            hidden = false;
        } else {
            edgeColor = 'purple';
            physics = false;
            hidden = false;
        }

        if (self.selected && other.selected) {
            self.saladManager.edges.update({
                id: edgeId,
                from: fromId,
                to: toId,
                color: {
                    color: edgeColor,
                    inherit: false,
                    highlight: edgeColor
                },
                physics: physics,
                dashes: false,
                hidden: hidden
            })
        } else if ((self.connected || other.connected) && (connectionType != 'lClash' && connectionType != 'uClash')) {
            self.saladManager.edges.update({
                id: edgeId,
                from: fromId,
                to: toId,
                color: {
                    color: edgeColor,
                    inherit: false,
                    highlight: edgeColor
                },
                physics: physics,
                dashes: true,
                hidden: hidden
            });
        } else {
            self.saladManager.edges.remove([edgeId]);
        }
    }

    self.render = function() {
        if (self.present) {

            // dirty node
            if ((!self.prevPresent) || (self.selected != self.prevSelected) || (self.locked != self.prevLocked) || (self.connected != self.prevConnected) || (self.highlighted != self.prevHighlighted) || (self.menu != self.prevMenu)) {
                var backgroundColor;
                if (self.selected) {
                    backgroundColor = self.color;
                } else {
                    backgroundColor = 'white';
                }

                var borderColor;
                var borderWidth;
                if (self.locked) {
                    borderColor = 'black';
                    borderWidth = 4;
                } else {
                    borderColor = self.color;
                    borderWidth = 2;
                }
                var size = 25;
                if (self.menu) size += 5;
                if (self.highlighted) size += 25;

                self.saladManager.nodes.update({
                    id: self.name,
                    label: self.name,
                    color: {
                        'background': backgroundColor,
                        'border': borderColor,
                        highlight: {
                            'background': backgroundColor,
                            'border': borderColor
                        },
                    },
                    borderWidth: borderWidth,
                    borderWidthSelected: borderWidth,
                    shape: 'dot',
                    size: size
                });
            }

            // dirty connections
            if ((self.selected != self.prevSelected) || (self.connected != self.prevConnected)) {
                self.ucNames.forEach(function(otherName) {
                    self.renderConnection(otherName, 'uc');
                });
                self.udNames.forEach(function(otherName) {
                    self.renderConnection(otherName, 'ud');
                });
                self.ldNames.forEach(function(otherName) {
                    self.renderConnection(otherName, 'ld');
                });
                self.uClashNames.forEach(function(otherName) {
                    self.renderConnection(otherName, 'uClash');
                });
                self.lClashNames.forEach(function(otherName) {
                    self.renderConnection(otherName, 'lClash');
                });

                var edgeId = self.id.toString() + '-' + self.id.toString();
                if (self.connected) {
                    self.saladManager.edges.update({
                        id: edgeId,
                        from: self.name,
                        to: self.name,
                        color: {
                            color: 'black',
                            inherit: false
                        },
                        physics: true,
                        dashes: true,
                    });
                } else {
                    self.saladManager.edges.remove([edgeId]);
                }
            }

            self.prevPresent = self.present;
            self.prevSelected = self.selected;
            self.prevLocked = self.locked;
            self.prevConnected = self.connected;
            self.prevHighlighted = self.highlighted;
            self.prevMenu = self.menu;
        }

        // should maybe make this happen regardless of prevPresent
        if (!self.present && self.prevPresent) {
            self.saladManager.nodes.remove([self.name]);
            self.prevPresent = self.present;
        }
    }

    self.clear = function() {
        self.present = false;
        self.selected = false;
        self.locked = false;
        self.connected = false;
        $('#present').selectivity('remove', self.name);
        self.render();
    }

    self.add = function(params={}) {
        self.present = true;
        self.selected = params.selected || false;
        self.locked = params.locked || false;
        self.connected = params.connected || false;
        $('#present').selectivity('add', self.name);
        self.render();
    }
}

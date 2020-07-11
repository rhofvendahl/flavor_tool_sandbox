var StirFryIngredient = function(stirFryManager, data) {
    var self = this;

    self.stirFryManager = stirFryManager;
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

    self.present = true;
    self.selected = false;
    self.locked = false;
    self.connected = false;

    if (data.stir_fry_veg == 'y') {
        self.color = 'green';
    } else if (data.stir_fry_fruit == 'y') {
        self.color = 'orange';
    } else if (data.stir_fry_protein == 'y') {
        self.color = 'brown';
    } else if (data.stir_fry_grain == 'y') {
        self.color = 'tan';
    } else {
        self.color = 'lightgrey';
    }

    self.renderConnection = function(otherName, connectionType) {
        var other = self.stirFryManager.getFromName(otherName);
        var edgeId;
        var fromId;
        var toId;
        if (self.id > other.id) {
            edgeId = other.id.toString() + '-' + self.id.toString();
            fromId = other.id
            toId = self.id
        } else {
            edgeId = self.id.toString() + '-' + other.id.toString();
            fromId = self.id
            toId = other.id
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
        // } else if (connectionType == 'lc') {
        //     edgeColor = 'purple';
        //     physics = false;//self.selected && other.selected;
        //     hidden = true;
        } else {
            edgeColor = 'purple';
            physics = false;
            hidden = false;
        }

        if (self.selected && other.selected) {
            self.stirFryManager.edges.update({
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
        } else if (self.connected || other.connected) {
            self.stirFryManager.edges.update({
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
            self.stirFryManager.edges.remove([edgeId]);
        }
    }

    self.render = function() {
        if (self.present) {
            $('#present').selectivity('add', self.name);
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
            self.stirFryManager.nodes.update({
                id: self.id,
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
                shape: 'dot'
            });

            self.ucNames.forEach(function(otherName) {
                self.renderConnection(otherName, 'uc');
            });
            self.udNames.forEach(function(otherName) {
                self.renderConnection(otherName, 'ud');
            });
            // self.lcNames.forEach(function(otherName) {
            //     self.renderConnection(otherName, 'lc');
            // });
            self.ldNames.forEach(function(otherName) {
                self.renderConnection(otherName, 'ld');
            });

            var edgeId = self.id.toString() + '-' + self.id.toString();
            if (self.connected) {
                self.stirFryManager.edges.update({
                    id: edgeId,
                    from: self.id,
                    to: self.id,
                    color: {
                        color: 'black',
                        inherit: false
                    },
                    physics: true,
                    dashes: true,
                });
            } else {
                self.stirFryManager.edges.remove([edgeId]);
            }
        } else {
            self.stirFryManager.nodes.remove([self.id]);
            $('#present').selectivity('remove', self.name);
        }
    }

    self.clear = function() {
        self.present = false;
        self.stirFryManager.presentSet.delete(self);
        self.selected = false;
        self.stirFryManager.selectedSet.delete(self);
        self.locked = false;
        self.stirFryManager.lockedSet.delete(self);
        self.connected = false;
        self.stirFryManager.connectedSet.delete(self);
    }
}

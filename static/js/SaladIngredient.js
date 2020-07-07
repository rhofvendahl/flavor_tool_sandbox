var SaladIngredient = function(saladManager, data) {
    var self = this;
    self.saladManager = saladManager;
    self.data = data;

    self.id = data.id;
    self.name = data.name;

    // self.lcIds = [];
    // self.ldIds = [];
    // self.ucIds = [];
    // self.udIds = [];
    // self.lIds = [];
    // self.uIds = [];
    // self.aIds = [];
    self.lcNames = data.lower_category_names;
    self.ldNames = data.lower_direct_names;
    self.ucames = data.upper_category_names;
    self.udNames = data.upper_direct_names;
    self.lNames = data.lower_names;
    self.uNames = data.upper_names;
    self.aNames = data.all_names;

    // self.lClashIds = [];
    // self.uclashIds = [];
    // self.aClashIds = [];
    self.lClashNames = data.lower_clashes_with_names;
    self.uclashNames = data.upper_clashes_with_names;
    self.aClashNames = data.all_clashes_with_names;

    self.present = true;
    self.selected = false;
    self.highlighted = false;

    // self.color = 'purple';
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

    // if (self.name == 'AVOCADO') {
    //     console.log(self.color, self.data.veg);
    // }
    // if (self.color == 'purple') {
    //     console.log('aaaaaaaaaaaaaaaa');
    //     console.log(self)
    // }

    // self.init = function() {
    //     for self.lcNames.forEach(name) {
    //         saladIngredient = self.saladManager.getFromName(name);
            // console.log(ingredient)
            // ingredient.selected = !ingredient.selected;
            // console.log(ingredient.selected)
            // ingredient.render();
    //
    //     };
    // };
    // self.render = function() {
    //     if (self.selected) {
    //         self.saladManager.nodes.update({
    //             id: self.id,
    //             label: self.name,
    //             color: {
    //                 'background': self.color,
    //                 // 'highlight': self.color,
    //                 'border': 'black',
    //                 highlight: {
    //                     'background': self.color,
    //                     'border': 'black'
    //                 },
    //             },
    //             hidden: !self.present,
    //             borderWidth: 1,
    //             shape: 'dot'
    //         });
    //
    //         self.udNames.forEach(function(name) {
    //             ingredient = self.saladManager.getFromName(name);
    //
    //             if (self.id > ingredient.id) {
    //                 edgeId = ingredient.id.toString() + '-' + self.id.toString();
    //                 fromId = ingredient.id
    //                 toId = self.id
    //             } else {
    //                 edgeId = self.id.toString() + '-' + ingredient.id.toString();
    //                 fromId = self.id
    //                 toId = ingredient.id
    //             }
    //             if (ingredient.selected) {
    //                 self.saladManager.edges.update({
    //                     id: edgeId,
    //                     from: fromId,
    //                     to: toId,
    //                     color: {
    //                         color: 'black',
    //                         inherit: false,
    //                     },
    //                     physics: true
    //                 })
    //             } else {
    //                 self.saladManager.edges.update({
    //                     id: edgeId,
    //                     from: fromId,
    //                     to: toId,
    //                     color: {
    //                         inherit: false,
    //                         highlight: 'red',
    //                     },
    //                     physics: false
    //                 });
    //             }
    //         });
    //     } else {
    //         self.saladManager.nodes.update({
    //             id: self.id,
    //             label: self.name,
    //             color: {
    //                 'background': 'white',
    //                 'border': 'black',
    //                 highlight: {
    //                     'background': 'white',
    //                     'border': 'black'
    //                 },
    //             },
    //             hidden: !self.present,
    //             borderWidth: 1,
    //             shape: 'dot'
    //         });
    //
    //         self.udNames.forEach(function(name) {
    //             ingredient = self.saladManager.getFromName(name);
    //
    //             if (self.id > ingredient.id) {
    //                 edgeId = ingredient.id.toString() + '-' + self.id.toString();
    //                 fromId = ingredient.id
    //                 toId = self.id
    //             } else {
    //                 edgeId = self.id.toString() + '-' + ingredient.id.toString();
    //                 fromId = self.id
    //                 toId = ingredient.id
    //             }
    //             if (ingredient.selected) {
    //                 self.saladManager.edges.update({
    //                     id: edgeId,
    //                     from: fromId,
    //                     to: toId,
    //                     color: {
    //                         // color: 'white',
    //                         inherit: false,
    //                         // highligiht: 'red'
    //                     },
    //                     physics: false
    //                 })
    //             } else {
    //                 self.saladManager.edges.remove([edgeId]);
    //             }
    //         });
    //     }
    // }

        // console.log('rendered')
        // if (self.dep != 'ROOT') {
        //     self.hidden = self.head.collapsed || self.head.hidden;
        // }
        //
        // self.parseTree.nodes.update({
        //     id: self.id,
        //     label: self.collapsed ? self.collapsedText : self.text,
        //     title: tagDescriptions[self.tag],
        //     color: self.color,
        //     hidden: self.hidden
        // });
        // self.parseTree.edges.update({
        //     id: self.id,
        //     from: self.headId,
        //     to: self.id,
        //     label: self.dep,
        //     title: depDescriptions[self.dep],
        //     arrows: 'to'
        // });

    self.render = function() {
        if (self.selected) {
            backgroundColor = self.color;
        } else {
            backgroundColor = 'white';
        }
        if (self.highlighted) {
            borderColor = 'black';
            borderWidth = 4;
        } else {
            borderColor = self.color;
            borderWidth = 2;
        }
        self.saladManager.nodes.update({
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
            hidden: !self.present,
            borderWidth: borderWidth,
            borderWidthSelected: borderWidth,
            shape: 'dot'
        });

        self.udNames.forEach(function(name) {
            other = self.saladManager.getFromName(name);
            if (self.id > other.id) {
                edgeId = other.id.toString() + '-' + self.id.toString();
                fromId = other.id
                toId = self.id
            } else {
                edgeId = self.id.toString() + '-' + other.id.toString();
                fromId = self.id
                toId = other.id
            }

            color = null
            remove = false
            if (self.selected && other.selected) {
                // console.log('both selected')
                self.saladManager.edges.update({
                    id: edgeId,
                    from: fromId,
                    to: toId,
                    color: {
                        color: 'black',
                        inherit: false,
                    },
                    physics: true,
                    dashes: false,
                    // length: 5
                })
            } else if (self.highlighted || other.highlighted) {
                // console.log('either highlighted')
                self.saladManager.edges.update({
                    id: edgeId,
                    from: fromId,
                    to: toId,
                    color: {
                        color: 'black',
                        inherit: false,
                    },
                    physics: true,
                    dashes: true,
                    // length: 100
                });
            } else {
                // console.log('nada')
                self.saladManager.edges.remove([edgeId]);
            }
        });
    }
}

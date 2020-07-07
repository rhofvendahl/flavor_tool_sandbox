var SaladManager = function() {
    var self = this;

    self.nodes = new vis.DataSet();
    self.edges = new vis.DataSet();

    var container = document.getElementById('network');
    var data = {nodes: self.nodes, edges: self.edges};
    var options = {
        // edges: {
        //     color: {
        //         //color:'#848484',
        //         // highlight:'#848484',
        //         // hover: '#d3d2cd',
        //         inherit: false,
        //         // opacity:1.0
        //     }
        // }
        nodes: {
            borderWidthSelected: 2
        },
        physics: {
            maxVelocity: 8
            // repulsion: {
            //     springConstant: .001
            // }
        }
    };
    self.network = new vis.Network(container, data, options);

    self.ingredients = [];
    self.presentSet = new Set();
    self.selectedSet = new Set();
    // self.highlightedIngredient = null;
    self.highlightedSet = new Set();

    self.getFromId = function(id) {
        var match = null;
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.id == id) match = ingredient;
        });
        return match;
    }

    self.getFromName = function(name) {
        var match = null;
        self.ingredients.forEach(function(ingredient) {
            // console.log('name1', ingredient.name, 'name2', name)
            if (ingredient.name == name) match = ingredient;
            // if (ingredient.name == 'AVOCADO') {
            //     console.log(ingredient);
            // }
        });
        return match;
    }

    self.importSubtree = function(tokens, token) {
        tokenNode = new TokenNode(self, token);
        self.tokenNodes.push(tokenNode);
        token.child_ids.forEach(function(childId) {
            self.importSubtree(tokens, tokens[childId])
        });
    }

    self.renderSubtree = function(tokenNode) {
        tokenNode.render();
        tokenNode.children.forEach(function(child) {
            self.renderSubtree(child);
        });
    }

    self.load = function() {
        // console.log('loading')
        fetch('/get_salad_ingredients')
        .then(function(response) {
            return response.json();
        }).then(function(ingredients) {
            // console.log(ingredients)
            self.ingredients = []
            ingredients.forEach(function(ingredient) {
                saladIngredient = new SaladIngredient(self, ingredient);
                self.ingredients.push(saladIngredient);
                self.presentSet.add(saladIngredient);
            });
        }).then(function() {
            self.ingredients.forEach(function(ingredient) {
                ingredient.render();
            });
        });
        // // remove additional nodes
        // self.nodes.getIds().forEach(function(id) {
        //   if (!self.getTokenNode(id)) {
        //     self.nodes.remove(id);
        //   }
        // });
    };

    self.clickTimeout = null

    self.network.on('click', function(properties) {
        // console.log('setting timeout')
        if (self.clickTimeout) {
            console.log('clearing timeout')
            clearTimeout(self.clickTimeout);
            self.clickTimeout = null;
        } else {
            console.log('setting timeout')
            self.clickTimeout = setTimeout(function() {
                console.log('timeout payload executing')
                if (properties.nodes.length > 0) {
                    ingredient = self.getFromId(properties.nodes[0]);
                    if (self.highlightedSet.has(ingredient)) {
                        // console.log('has')
                        ingredient.highlighted = false;
                        self.highlightedSet.delete(ingredient);
                    } else {
                        // console.log('hasnt')
                        ingredient.highlighted = true;
                        self.highlightedSet.add(ingredient);
                    }
                    ingredient.render();
                    // console.log(self.highlightedIngredient);
                }
                self.clickTimeout = null;
            }, 200);
        }
        // console.log('clicked', properties)
    });
    self.network.on('doubleClick', function(properties) {
        // if (self.clickTimeout) {
        //     console.log('clearing timeout')
        //     clearTimeout(self.clickTimeout);
        //
        // }
        // console.log('double clicked', properties)
        if (properties.nodes.length > 0) {
            ingredient = self.getFromId(properties.nodes[0]);
            if (ingredient.selected) {
                ingredient.selected = false;
                self.selectedSet.delete(ingredient)
            } else {
                ingredient.selected = true;
                self.selectedSet.add(ingredient)
            }
            // console.log(ingredient)
            // ingredient.selected = !ingredient.selected;
            // console.log(ingredient.selected)
            ingredient.render();
        }
    });
}

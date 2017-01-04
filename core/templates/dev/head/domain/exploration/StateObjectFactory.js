// Copyright 2015 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Factory for creating new frontend instances of State
 * domain objects.
 */

oppia.factory('StateObjectFactory', [
  'AnswerGroupObjectFactory', 
  function(AnswerGroupObjectFactory) {
  var State = function(name, content, interaction, paramChanges) {
    console.log(paramChanges);
    this.name = name;
    this.content = content;
    this.interaction = interaction;
    this.paramChanges = paramChanges;

    var answerGroups = [];
    for (var answerGroup in interaction.answer_groups) {
      console.log(interaction.answer_groups);
      var answerGroupData = interaction.answer_groups[answerGroup];
      console.log(angular.copy(answerGroupData));
      answerGroups.push(
        AnswerGroupObjectFactory.create(
          answerGroupData.rule_specs, answerGroupData.outcome));
    }
    this.interaction.answer_groups = answerGroups;
    console.log(angular.copy(this));
  };

  // Instance methods.
  State.prototype.toBackendDict = function() {
    // var answerGroups = [];
    // console.log(angular.copy(this.interaction.answer_groups));
    // for (answer_group in this.interaction.answer_groups) {
    //   answerGroups.push(this.interaction
    //     .answer_groups[answer_group].toBackendDict());
    // }
    // this.interaction.answer_groups = answerGroups;

    return {
      content: this.content,
      interaction: this.interaction,
      param_changes: this.paramChanges
    };
  };

  // Static class methods. Note that "this" is not available in
  // static contexts.
  State.create = function(stateName, stateDict) {
    console.log(angular.copy(stateDict))
    console.log(angular.copy(stateDict.param_changes));
    return new State(
      stateName,
      stateDict.content,
      stateDict.interaction,
      stateDict.param_changes);
  };

  return State;
}]);

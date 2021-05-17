'use strict';
const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class VirtualRules extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      // define association here
    }
  };
  VirtualRules.init({
    UserName: DataTypes.STRING,
    Currency: DataTypes.STRING,
    AllocatedBudget: DataTypes.DOUBLE,
    BuyPercent: DataTypes.DOUBLE,
    SellPercent: DataTypes.DOUBLE,
    StartPrice: DataTypes.DOUBLE,
    IsActif: DataTypes.BOOLEAN
  }, {
    sequelize,
    modelName: 'VirtualRules',
  });
  return VirtualRules;
};
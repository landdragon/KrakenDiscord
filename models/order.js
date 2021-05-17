'use strict';
const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class Order extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      // define association here
    }
  };
  Order.init({
    UserName: DataTypes.STRING,
    Way: DataTypes.STRING,
    Quantity: DataTypes.DOUBLE,
    Price: DataTypes.DOUBLE,
    Currency: DataTypes.STRING,
    From: DataTypes.STRING,
    State: DataTypes.STRING
  }, {
    sequelize,
    modelName: 'Order',
  });
  return Order;
};
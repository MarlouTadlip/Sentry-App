import { useThemeColors } from "@/hooks/useThemeColors";
import { useToast } from "@/hooks/useToast";
import { lovedOneService, LovedOne, User } from "@/services/lovedOne.service";
import { extractErrorMessage } from "@/lib/errorUtils";
import { 
  Plus, 
  Users, 
  Trash2, 
  Bell, 
  BellOff, 
  Mail,
  Search,
  UserPlus
} from "@tamagui/lucide-icons";
import React, { useState, useEffect, useCallback } from "react";
import { 
  Button, 
  Card, 
  ScrollView, 
  Text, 
  XStack, 
  YStack, 
  Input,
  Switch,
  Spinner
} from "tamagui";

const contacts = () => {
  const colors = useThemeColors();
  const toast = useToast();
  const [lovedOnes, setLovedOnes] = useState<LovedOne[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [emailInput, setEmailInput] = useState("");
  const [isAlertedDefault, setIsAlertedDefault] = useState(false);
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set());
  const [togglingIds, setTogglingIds] = useState<Set<number>>(new Set());
  
  // Search functionality
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  // Fetch loved ones on mount
  useEffect(() => {
    fetchLovedOnes();
  }, []);

  // Debounced search function
  const performSearch = useCallback(async (query: string) => {
    if (!query || query.trim().length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await lovedOneService.searchUsers(query.trim(), 10);
      setSearchResults(response.users);
    } catch (error: any) {
      console.error("❌ Failed to search users:", error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Handle search input change with debounce
  useEffect(() => {
    // Clear previous timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    // Set new timeout for debounced search
    const timeout = setTimeout(() => {
      performSearch(searchQuery);
    }, 500); // 500ms debounce

    setSearchTimeout(timeout);

    // Cleanup
    return () => {
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, [searchQuery, performSearch]);

  const fetchLovedOnes = async () => {
    setIsLoading(true);
    try {
      const response = await lovedOneService.getLovedOnes();
      setLovedOnes(response.loved_ones);
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error);
      console.error("❌ Failed to fetch loved ones:", error);
      toast.showError("Failed to Load", errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddLovedOne = async (email?: string) => {
    const emailToAdd = email || emailInput.trim();
    if (!emailToAdd) {
      toast.showError("Invalid Email", "Please enter an email address");
      return;
    }

    setIsAdding(true);
    try {
      const response = await lovedOneService.addLovedOne(emailToAdd, isAlertedDefault);
      toast.showSuccess("Contact Added", response.message);
      setEmailInput("");
      setSearchQuery("");
      setSearchResults([]);
      setShowAddForm(false);
      setIsAlertedDefault(false);
      await fetchLovedOnes(); // Refresh list
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error);
      console.error("❌ Failed to add loved one:", error);
      toast.showError("Add Failed", errorMessage);
    } finally {
      setIsAdding(false);
    }
  };

  const handleSelectUser = (user: User) => {
    handleAddLovedOne(user.email);
  };

  const handleDeleteLovedOne = async (lovedOneId: number, email: string) => {
    setDeletingIds(prev => new Set(prev).add(lovedOneId));
    try {
      const response = await lovedOneService.deleteLovedOne(lovedOneId);
      toast.showSuccess("Contact Removed", response.message);
      await fetchLovedOnes(); // Refresh list
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error);
      console.error("❌ Failed to delete loved one:", error);
      toast.showError("Delete Failed", errorMessage);
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(lovedOneId);
        return newSet;
      });
    }
  };

  const handleToggleAlerted = async (lovedOneId: number) => {
    setTogglingIds(prev => new Set(prev).add(lovedOneId));
    try {
      const response = await lovedOneService.toggleLovedOneAlerted(lovedOneId);
      toast.showSuccess("Settings Updated", response.message);
      await fetchLovedOnes(); // Refresh list
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error);
      console.error("❌ Failed to toggle alerted status:", error);
      toast.showError("Update Failed", errorMessage);
    } finally {
      setTogglingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(lovedOneId);
        return newSet;
      });
    }
  };

  return (
    <ScrollView style={{ backgroundColor: colors.background }}>
      <YStack padding={"$4"} gap={"$4"}>
        {/* Header Card */}
        <Card
          elevate
          bordered
          animation={"bouncy"}
          borderColor={colors.border}
          padded
          gap={"$4"}
          enterStyle={{ opacity: 0, y: 10 }}
          backgroundColor={colors.cardBackground}
        >
          <XStack justifyContent="space-between" alignItems="center">
            <XStack gap={"$2"} alignItems="center">
              <Users color={colors.primary} />
              <Text fontSize={"$6"} fontWeight="bold" color={colors.text}>
                Emergency Contacts
              </Text>
            </XStack>
            <Button
              backgroundColor={colors.primary}
              onPress={() => setShowAddForm(!showAddForm)}
              disabled={isAdding}
            >
              <Plus color="#ffffff" />
              <Text color="#ffffff">{showAddForm ? "Cancel" : "Add"}</Text>
            </Button>
          </XStack>

          {/* Add Form */}
          {showAddForm && (
            <YStack gap={"$3"} paddingTop={"$2"}>
              <YStack gap={"$2"}>
                <Text color={colors.text} fontSize={"$3"}>
                  Search Users
                </Text>
                <XStack gap={"$2"} alignItems="center">
                  <Search color={colors.text + "60"} size={18} />
                  <Input
                    flex={1}
                    placeholder="Search by name or email..."
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    autoCapitalize="none"
                    autoCorrect={false}
                    backgroundColor={colors.background}
                    borderColor={colors.border}
                    color={colors.text}
                    placeholderTextColor={colors.text + "80"}
                  />
                  {isSearching && (
                    <Spinner size="small" color={colors.primary} />
                  )}
                </XStack>
              </YStack>

              {/* Search Results */}
              {searchQuery.length >= 2 && (
                <YStack gap={"$2"} maxHeight={200}>
                  <ScrollView>
                    {searchResults.length === 0 && !isSearching ? (
                      <Card
                        bordered
                        borderColor={colors.border}
                        padded
                        backgroundColor={colors.background}
                      >
                        <Text color={colors.text + "80"} fontSize={"$3"} textAlign="center">
                          No users found
                        </Text>
                      </Card>
                    ) : (
                      searchResults.map((user) => {
                        // Check if user is already a loved one
                        const isAlreadyLovedOne = lovedOnes.some(
                          (lo) => lo.loved_one.email === user.email
                        );

                        return (
                          <Card
                            key={user.id}
                            bordered
                            borderColor={colors.border}
                            padded
                            backgroundColor={colors.background}
                            pressStyle={{ opacity: 0.7 }}
                            onPress={() => !isAlreadyLovedOne && handleSelectUser(user)}
                            disabled={isAlreadyLovedOne || isAdding}
                          >
                            <XStack gap={"$3"} alignItems="center">
                              <Mail color={colors.primary} size={18} />
                              <YStack flex={1}>
                                <Text color={colors.text} fontSize={"$4"} fontWeight="600">
                                  {user.first_name} {user.last_name}
                                </Text>
                                <Text color={colors.text + "80"} fontSize={"$3"}>
                                  {user.email}
                                </Text>
                              </YStack>
                              {isAlreadyLovedOne ? (
                                <Text color={colors.text + "60"} fontSize={"$2"}>
                                  Already added
                                </Text>
                              ) : (
                                <Button
                                  size="$3"
                                  backgroundColor={colors.primary}
                                  onPress={() => handleSelectUser(user)}
                                  disabled={isAdding}
                                >
                                  <UserPlus color="#ffffff" size={16} />
                                </Button>
                              )}
                            </XStack>
                          </Card>
                        );
                      })
                    )}
                  </ScrollView>
                </YStack>
              )}

              {/* Manual Email Input (fallback) */}
              <YStack gap={"$2"}>
                <Text color={colors.text} fontSize={"$3"}>
                  Or enter email manually
                </Text>
                <Input
                  placeholder="Enter email address"
                  value={emailInput}
                  onChangeText={setEmailInput}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  backgroundColor={colors.background}
                  borderColor={colors.border}
                  color={colors.text}
                  placeholderTextColor={colors.text + "80"}
                />
              </YStack>

              <XStack gap={"$3"} alignItems="center">
                <Switch
                  checked={isAlertedDefault}
                  onCheckedChange={setIsAlertedDefault}
                  size="$4"
                />
                <Text color={colors.text} fontSize={"$3"}>
                  Alert this contact when crash is detected
                </Text>
              </XStack>
              <Button
                backgroundColor={colors.primary}
                onPress={() => handleAddLovedOne()}
                disabled={isAdding || (!emailInput.trim() && searchResults.length === 0)}
              >
                {isAdding ? (
                  <Spinner size="small" color="#ffffff" />
                ) : (
                  <>
                    <Plus color="#ffffff" />
                    <Text color="#ffffff">Add Contact</Text>
                  </>
                )}
              </Button>
            </YStack>
          )}
        </Card>

        {/* Loading State */}
        {isLoading && (
          <Card
            bordered
            borderColor={colors.border}
            padded
            backgroundColor={colors.cardBackground}
          >
            <XStack gap={"$3"} alignItems="center" justifyContent="center">
              <Spinner size="small" color={colors.primary} />
              <Text color={colors.text}>Loading contacts...</Text>
            </XStack>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && lovedOnes.length === 0 && (
          <Card
            bordered
            borderColor={colors.border}
            padded
            backgroundColor={colors.cardBackground}
          >
            <YStack gap={"$3"} alignItems="center" paddingVertical={"$4"}>
              <Users size={48} color={colors.text + "60"} />
              <Text color={colors.text} fontSize={"$5"} textAlign="center">
                No Emergency Contacts
              </Text>
              <Text color={colors.text + "80"} fontSize={"$3"} textAlign="center">
                Add contacts who should be notified in case of emergency
              </Text>
            </YStack>
          </Card>
        )}

        {/* Loved Ones List */}
        {!isLoading && lovedOnes.length > 0 && (
          <YStack gap={"$3"}>
            {lovedOnes.map((lovedOne) => {
              const isDeleting = deletingIds.has(lovedOne.id);
              const isToggling = togglingIds.has(lovedOne.id);
              
              return (
                <Card
                  key={lovedOne.id}
                  elevate
                  bordered
                  animation={"bouncy"}
                  borderColor={colors.border}
                  padded
                  gap={"$3"}
                  enterStyle={{ opacity: 0, y: 10 }}
                  backgroundColor={colors.cardBackground}
                >
                  <XStack justifyContent="space-between" alignItems="center">
                    <XStack gap={"$3"} alignItems="center" flex={1}>
                      <Mail color={colors.primary} size={20} />
                      <YStack flex={1}>
                        <Text color={colors.text} fontSize={"$4"} fontWeight="600">
                          {lovedOne.loved_one.first_name} {lovedOne.loved_one.last_name}
                        </Text>
                        <Text color={colors.text + "80"} fontSize={"$3"}>
                          {lovedOne.loved_one.email}
                        </Text>
                      </YStack>
                    </XStack>
                  </XStack>

                  <XStack gap={"$3"} alignItems="center" justifyContent="space-between">
                    <XStack gap={"$2"} alignItems="center" flex={1}>
                      {isToggling ? (
                        <Spinner size="small" color={colors.primary} />
                      ) : (
                        <>
                          {lovedOne.is_alerted ? (
                            <Bell color={colors.primary} size={18} />
                          ) : (
                            <BellOff color={colors.text + "60"} size={18} />
                          )}
                        </>
                      )}
                      <Text color={colors.text} fontSize={"$3"} flex={1}>
                        {lovedOne.is_alerted ? "Will be alerted" : "Will not be alerted"}
                      </Text>
                    </XStack>
                    <XStack gap={"$2"}>
                      <Button
                        size="$3"
                        backgroundColor={lovedOne.is_alerted ? colors.primary + "40" : colors.primary}
                        onPress={() => handleToggleAlerted(lovedOne.id)}
                        disabled={isToggling || isDeleting}
                      >
                        {lovedOne.is_alerted ? (
                          <BellOff color={lovedOne.is_alerted ? colors.primary : "#ffffff"} size={16} />
                        ) : (
                          <Bell color="#ffffff" size={16} />
                        )}
                      </Button>
                      <Button
                        size="$3"
                        backgroundColor="#ef4444"
                        onPress={() => handleDeleteLovedOne(lovedOne.id, lovedOne.loved_one.email)}
                        disabled={isDeleting || isToggling}
                      >
                        {isDeleting ? (
                          <Spinner size="small" color="#ffffff" />
                        ) : (
                          <Trash2 color="#ffffff" size={16} />
                        )}
                      </Button>
                    </XStack>
                  </XStack>
                </Card>
              );
            })}
          </YStack>
        )}
      </YStack>
    </ScrollView>
  );
};

export default contacts;
